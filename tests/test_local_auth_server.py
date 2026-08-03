import http.client
import json
from http.server import HTTPServer
from pathlib import Path
import tempfile
import threading
import unittest

from scripts.serve_retinova import create_handler


class FakePredictor:
    def predict(self, image_bytes):
        return {"prediction": "N", "received_bytes": len(image_bytes)}


class LocalAuthServerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        dashboard = Path(self.temporary.name)
        (dashboard / "index.html").write_text("Retinova", encoding="utf-8")
        handler = create_handler(FakePredictor(), dashboard, team_passcode="correct horse")
        self.server = HTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port)

    def tearDown(self):
        self.connection.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temporary.cleanup()

    def request_json(self, method, path, payload=None, headers=None):
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request_headers = {"Content-Type": "application/json"} if payload is not None else {}
        request_headers.update(headers or {})
        self.connection.request(method, path, body=body, headers=request_headers)
        response = self.connection.getresponse()
        result = json.loads(response.read())
        return response, result

    def test_prediction_requires_a_valid_http_only_session(self):
        response, result = self.request_json("POST", "/predict", {"image": "aGVsbG8="})
        self.assertEqual(response.status, 401)
        self.assertEqual(result["error"], "team login required")

        response, result = self.request_json("POST", "/session", {"passcode": "wrong"})
        self.assertEqual(response.status, 401)
        self.assertEqual(result["error"], "invalid team passcode")

        response, result = self.request_json("POST", "/session", {"passcode": "correct horse"})
        self.assertEqual(response.status, 200)
        self.assertTrue(result["authenticated"])
        cookie = response.getheader("Set-Cookie")
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=Strict", cookie)
        session_cookie = cookie.split(";", 1)[0]

        response, result = self.request_json(
            "POST", "/predict", {"image": "aGVsbG8="}, {"Cookie": session_cookie}
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(result, {"prediction": "N", "received_bytes": 5})

        response, result = self.request_json("DELETE", "/session", headers={"Cookie": session_cookie})
        self.assertEqual(response.status, 200)
        self.assertFalse(result["authenticated"])

        response, _ = self.request_json(
            "POST", "/predict", {"image": "aGVsbG8="}, {"Cookie": session_cookie}
        )
        self.assertEqual(response.status, 401)


if __name__ == "__main__":
    unittest.main()
