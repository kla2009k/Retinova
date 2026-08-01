"""Serve the Retinova UI with local checkpoint inference on localhost only."""
import argparse
import base64
import binascii
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from retinova_ml.inference import RetinovaPredictor


MAX_REQUEST_BYTES = 14_000_000


def create_handler(predictor, dashboard):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(dashboard), **kwargs)

        def send_json(self, status, payload):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/health":
                self.send_json(200, {"status": "ready", "mode": "local-research-model"})
                return
            super().do_GET()

        def do_POST(self):
            if self.path != "/predict":
                self.send_json(404, {"error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > MAX_REQUEST_BYTES:
                    raise ValueError("invalid request size")
                payload = json.loads(self.rfile.read(length))
                encoded = payload.get("image", "")
                if not isinstance(encoded, str):
                    raise ValueError("image must be a base64 string")
                if "," in encoded[:100]:
                    encoded = encoded.split(",", 1)[1]
                image_bytes = base64.b64decode(encoded, validate=True)
                self.send_json(200, predictor.predict(image_bytes))
            except (ValueError, json.JSONDecodeError, binascii.Error) as error:
                self.send_json(400, {"error": str(error)})
            except Exception:
                self.send_json(500, {"error": "local inference failed"})

    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--dashboard", default="dashboard")
    args = parser.parse_args()
    predictor = RetinovaPredictor(args.checkpoint)
    dashboard = Path(args.dashboard).resolve()
    handler = create_handler(predictor, dashboard)
    # Single-request serving prevents concurrent hooks from sharing model state.
    with HTTPServer(("127.0.0.1", args.port), handler) as server:
        print(f"Retinova local research server: http://127.0.0.1:{args.port}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
