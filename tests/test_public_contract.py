from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
JS = (ROOT / "dashboard" / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "dashboard" / "styles.css").read_text(encoding="utf-8")
SERVER = (ROOT / "dashboard" / "serve_with_log.py").read_text(encoding="utf-8")


class PublicContractTests(unittest.TestCase):
    def test_public_brand_and_scope_are_explicit(self):
        self.assertIn("Retinova", HTML)
        self.assertRegex(HTML, r"จอประสาทตา|retinal fundus")
        self.assertIn("ไม่ใช่การวินิจฉัย", HTML)

    def test_public_preview_has_no_unverified_marketing_metrics(self):
        public = HTML + JS
        self.assertNotIn("94.2%", public)
        self.assertNotIn("20,000+", public)
        self.assertNotRegex(public, r"private\s*&\s*encrypted|ข้อมูล.*เข้ารหัส")

    def test_dashboard_restores_the_reference_application_shell(self):
        self.assertIn('class="app-shell"', HTML)
        self.assertIn('class="sidebar"', HTML)
        self.assertIn('class="topbar"', HTML)
        for view in ("home", "analyze", "history", "eye-health", "evidence"):
            self.assertIn(f'data-view="{view}"', HTML)
            self.assertIn(f'id="view-{view}"', HTML)
        self.assertIn("--navy-950:#081c2b", re.sub(r"\s+", "", CSS))
        self.assertIn("--cyan:#52c7df", re.sub(r"\s+", "", CSS))

    def test_dashboard_navigation_is_button_based_and_scripted(self):
        self.assertRegex(HTML, r'<button[^>]+data-view="analyze"')
        self.assertIn("showView", JS)
        self.assertIn("history.replaceState", JS)

    def test_redesign_keeps_truthful_public_and_local_modes(self):
        public = HTML + JS
        self.assertIn("PUBLIC PREVIEW", public)
        self.assertIn("localModelReady", JS)
        self.assertIn('id="modelOutput"', HTML)
        self.assertNotIn("Eye health score", public)
        self.assertNotIn("AI Confidence", public)

    def test_welcome_gate_supports_guest_and_optional_local_team_login(self):
        self.assertIn('id="welcomeGate"', HTML)
        self.assertIn('id="guestButton"', HTML)
        self.assertIn('id="teamLoginForm"', HTML)
        self.assertRegex(HTML, r'id="teamPasscode"[^>]+autocomplete="current-password"')
        self.assertIn("fetch('/session'", JS)
        self.assertIn("credentials: 'same-origin'", JS)
        self.assertNotIn("localStorage", JS)
        self.assertNotIn("sessionStorage", JS)

    def test_history_is_session_only_and_never_stores_images(self):
        self.assertIn('id="view-history"', HTML)
        self.assertIn('id="historyList"', HTML)
        self.assertIn("const sessionHistory = []", JS)
        self.assertIn("MAX_SESSION_RESULTS", JS)
        self.assertIn("renderSessionHistory", JS)
        self.assertNotRegex(JS, r"sessionHistory\.push\([^)]*(image|gradcam)")

    def test_real_gradcam_comparison_has_no_synthetic_heatmap(self):
        self.assertIn('id="comparisonSlider"', HTML)
        self.assertIn('id="originalCompareImage"', HTML)
        self.assertIn('id="gradcamCompareImage"', HTML)
        self.assertIn("clipPath", JS)
        self.assertNotIn("radial-gradient", JS)

    def test_optional_local_auth_uses_server_side_http_only_sessions(self):
        server = (ROOT / "scripts" / "serve_retinova.py").read_text(encoding="utf-8")
        self.assertIn('os.environ.get("RETINOVA_TEAM_PASSCODE")', server)
        self.assertIn("hmac.compare_digest", server)
        self.assertIn("secrets.token_urlsafe", server)
        self.assertIn("HttpOnly", server)
        self.assertIn("SameSite=Strict", server)
        self.assertIn('self.path == "/session"', server)

    def test_hidden_states_cannot_be_overridden_by_component_css(self):
        css = (ROOT / "dashboard" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("[hidden]{display:none!important}", HTML + css)

    def test_no_credential_like_literal_is_committed(self):
        source = JS + SERVER
        self.assertNotRegex(source, r"api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_-]{16,}['\"]")
        self.assertNotRegex(source, r"ROBOFLOW_API_KEY[^\n]+\bor\s+['\"]")

    def test_chat_does_not_render_user_html(self):
        self.assertNotIn("insertAdjacentHTML", JS)

    def test_model_api_is_probed_only_on_localhost(self):
        self.assertIn("['127.0.0.1', 'localhost'].includes(location.hostname)", JS)
        self.assertIn("fetch('/predict'", JS)

    def test_local_model_server_is_loopback_and_single_request(self):
        server = (ROOT / "scripts" / "serve_retinova.py").read_text(encoding="utf-8")
        self.assertIn('HTTPServer(("127.0.0.1", args.port)', server)
        self.assertNotIn("ThreadingHTTPServer", server)

    def test_server_contract_uses_environment_and_documented_port(self):
        self.assertIn('os.environ.get("ROBOFLOW_API_KEY")', SERVER)
        self.assertIn('int(os.environ.get("PORT", "8000"))', SERVER)

    def test_pages_workflow_publishes_only_dashboard(self):
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
        self.assertIn("actions/deploy-pages@v4", workflow)
        self.assertRegex(workflow, r"path:\s*['\"]?dashboard")


if __name__ == "__main__":
    unittest.main()
