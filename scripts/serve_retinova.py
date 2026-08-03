"""Serve the Retinova UI with local checkpoint inference on localhost only."""
import argparse
import base64
import binascii
from http.cookies import SimpleCookie
import hmac
import json
import os
import secrets
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import time

from retinova_ml.inference import RetinovaPredictor


MAX_REQUEST_BYTES = 14_000_000
MAX_LOGIN_BYTES = 4_096
SESSION_SECONDS = 8 * 60 * 60
LOGIN_WINDOW_SECONDS = 60
MAX_LOGIN_ATTEMPTS = 5
MAX_ACTIVE_SESSIONS = 32
MIN_TEAM_PASSCODE_LENGTH = 12


def create_handler(predictor, dashboard, team_passcode=None):
    sessions = {}
    failed_logins = []

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(dashboard), **kwargs)

        def send_json(self, status, payload, headers=None):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            for name, value in (headers or {}).items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(body)

        def session_token(self):
            cookie = SimpleCookie(self.headers.get("Cookie", ""))
            value = cookie.get("retinova_session")
            return value.value if value else None

        def authenticated(self):
            if not team_passcode:
                return True
            token = self.session_token()
            expires_at = sessions.get(token)
            if not expires_at:
                return False
            if expires_at <= time.monotonic():
                sessions.pop(token, None)
                return False
            return True

        def read_json(self, maximum_bytes):
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > maximum_bytes:
                raise ValueError("invalid request size")
            return json.loads(self.rfile.read(length))

        def do_GET(self):
            if self.path == "/health":
                self.send_json(
                    200,
                    {
                        "status": "ready",
                        "mode": "local-research-model",
                        "auth_mode": "team-passcode" if team_passcode else "open-local",
                        "authenticated": self.authenticated(),
                    },
                )
                return
            if self.path == "/session":
                self.send_json(200, {"authenticated": self.authenticated()})
                return
            super().do_GET()

        def do_POST(self):
            if self.path == "/session":
                self.create_session()
                return
            if self.path != "/predict":
                self.send_json(404, {"error": "not found"})
                return
            if not self.authenticated():
                self.send_json(401, {"error": "team login required"})
                return
            try:
                payload = self.read_json(MAX_REQUEST_BYTES)
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

        def create_session(self):
            now = time.monotonic()
            failed_logins[:] = [
                attempt
                for attempt in failed_logins
                if now - attempt < LOGIN_WINDOW_SECONDS
            ]
            if len(failed_logins) >= MAX_LOGIN_ATTEMPTS:
                self.send_json(429, {"error": "too many login attempts; wait one minute"})
                return
            try:
                payload = self.read_json(MAX_LOGIN_BYTES)
                supplied = payload.get("passcode", "")
                if not isinstance(supplied, str) or not team_passcode:
                    raise ValueError("team login is not configured")
                if not hmac.compare_digest(supplied, team_passcode):
                    failed_logins.append(now)
                    self.send_json(401, {"error": "invalid team passcode"})
                    return
                failed_logins.clear()
                expired_tokens = [
                    session_token
                    for session_token, expiry in sessions.items()
                    if expiry <= now
                ]
                for expired_token in expired_tokens:
                    sessions.pop(expired_token, None)
                if len(sessions) >= MAX_ACTIVE_SESSIONS:
                    sessions.pop(min(sessions, key=sessions.get), None)
                token = secrets.token_urlsafe(32)
                sessions[token] = now + SESSION_SECONDS
                cookie = (
                    f"retinova_session={token}; HttpOnly; SameSite=Strict; "
                    f"Path=/; Max-Age={SESSION_SECONDS}"
                )
                self.send_json(200, {"authenticated": True, "role": "local-team"}, {"Set-Cookie": cookie})
            except (ValueError, json.JSONDecodeError) as error:
                self.send_json(400, {"error": str(error)})

        def do_DELETE(self):
            if self.path != "/session":
                self.send_json(404, {"error": "not found"})
                return
            token = self.session_token()
            if token:
                sessions.pop(token, None)
            cookie = "retinova_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0"
            self.send_json(200, {"authenticated": False}, {"Set-Cookie": cookie})

    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--dashboard", default="dashboard")
    args = parser.parse_args()
    predictor = RetinovaPredictor(args.checkpoint)
    dashboard = Path(args.dashboard).resolve()
    team_passcode = os.environ.get("RETINOVA_TEAM_PASSCODE")
    if team_passcode and len(team_passcode) < MIN_TEAM_PASSCODE_LENGTH:
        parser.error(
            f"RETINOVA_TEAM_PASSCODE must contain at least {MIN_TEAM_PASSCODE_LENGTH} characters"
        )
    handler = create_handler(predictor, dashboard, team_passcode=team_passcode)
    # Single-request serving prevents concurrent hooks from sharing model state.
    with HTTPServer(("127.0.0.1", args.port), handler) as server:
        print(f"Retinova local research server: http://127.0.0.1:{args.port}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
