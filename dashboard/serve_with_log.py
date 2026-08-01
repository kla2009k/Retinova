"""Local Retinova preview server and optional Roboflow proxy.

Run from the dashboard directory with ``python serve_with_log.py`` and open
http://localhost:8000. Live inference is available only when
ROBOFLOW_API_KEY is set; the public GitHub Pages site never receives the key.
"""
import datetime
import http.server
import json
import os
from pathlib import Path
import socketserver

import requests


ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", "8000"))
MODEL = os.environ.get("ROBOFLOW_MODEL", "visioncare-odir/2")
KEY = os.environ.get("ROBOFLOW_API_KEY")
LOGFILE = ROOT / "test_log.jsonl"
os.chdir(ROOT)


def write_log(record):
    record["time"] = datetime.datetime.now(datetime.UTC).isoformat()
    with LOGFILE.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")


def call_roboflow(image_base64):
    if not KEY:
        raise RuntimeError("ROBOFLOW_API_KEY is not configured")
    url = f"https://serverless.roboflow.com/{MODEL}"
    response = requests.post(
        url,
        params={"api_key": KEY},
        data=image_base64,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=40,
    )
    response.raise_for_status()
    return response.json()


class Handler(http.server.SimpleHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/predict":
            self.send_json(404, {"error": "not found"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > 14_000_000:
                raise ValueError("invalid request size")
            payload = json.loads(self.rfile.read(size))
            encoded = payload.get("image", "")
            if "," in encoded[:100]:
                encoded = encoded.split(",", 1)[1]
            result = call_roboflow(encoded)
            write_log({"event": "predict", "model": MODEL, "top": result.get("top")})
            result["model"] = MODEL
            self.send_json(200, result)
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json(400, {"error": str(error)})
        except RuntimeError as error:
            self.send_json(503, {"error": str(error)})
        except requests.RequestException:
            self.send_json(502, {"error": "inference provider unavailable"})

    def log_message(self, message, *args):
        print(message % args)


if __name__ == "__main__":
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as server:
        print(f"Retinova preview: http://127.0.0.1:{PORT}")
        server.serve_forever()
