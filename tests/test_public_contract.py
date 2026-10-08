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
        for view in ("home", "analyze", "history", "eye-health", "evidence", "settings"):
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

    def test_reference_layout_has_real_content_in_each_poster_surface(self):
        for class_name in (
            "latest-scan-panel",
            "analysis-summary-panel",
            "history-chart-panel",
            "capture-details-panel",
        ):
            self.assertRegex(HTML, rf'class="[^"]*\b{class_name}\b')
        self.assertIn('src="assets/anatomy.jpg"', HTML)
        self.assertIn('src="assets/fundus-pair.jpg"', HTML)

    def test_poster_viewport_uses_the_measured_reference_geometry(self):
        compact_css = re.sub(r"\s+", "", CSS)
        self.assertIn("--poster-sidebar:167px", compact_css)
        self.assertIn("--poster-gap:15px", compact_css)
        self.assertIn("--poster-right:27px", compact_css)
        self.assertIn("--poster-topbar:51px", compact_css)
        self.assertIn("--poster-hero:249px", compact_css)
        self.assertIn("appShell.dataset.activeView=nextView", re.sub(r"\s+", "", JS))

    def test_reference_copy_and_mobile_capture_remain_available(self):
        self.assertIn('data-en="Care for your eye health with Artificial Intelligence"', HTML)
        self.assertIn('class="sample-row"', HTML)
        self.assertIn('id="openCameraButton"', HTML)
        self.assertIn("supportedLanguages = ['th', 'en', 'zh']", JS)
        self.assertIn('data-welcome-language="zh"', HTML)
        self.assertIn('data-th="เริ่มวิเคราะห์ดวงตา"', HTML)

    def test_reference_layout_never_reintroduces_fabricated_poster_results(self):
        public = HTML + JS
        self.assertNotIn("Eye Health Score", public)
        self.assertNotIn("คะแนนสุขภาพตา", public)
        self.assertNotRegex(public, r">\s*99%\s*<")
        self.assertNotIn("progressionSeries", JS)
        self.assertIn("No session results", public)

    def test_welcome_gate_supports_guest_and_optional_local_team_login(self):
        self.assertIn('id="welcomeGate"', HTML)
        self.assertIn('id="guestButton"', HTML)
        self.assertIn('id="teamLoginForm"', HTML)
        self.assertIn('href="https://retinova-f70k.onrender.com/"', HTML)
        self.assertRegex(HTML, r'id="teamPasscode"[^>]+autocomplete="current-password"')
        self.assertIn("fetch('/session'", JS)
        self.assertIn("credentials: 'same-origin'", JS)
        self.assertNotRegex(JS, r"localStorage\.setItem\([^,]+,\s*(?:selectedFile|teamPasscode|sessionHistory)")
        self.assertNotIn("sessionStorage", JS)

    def test_history_is_session_only_and_never_stores_images(self):
        self.assertIn('id="view-history"', HTML)
        self.assertIn('id="historyList"', HTML)
        self.assertIn("const sessionHistory = []", JS)
        self.assertIn("MAX_SESSION_RESULTS", JS)
        self.assertIn("renderSessionHistory", JS)
        self.assertNotRegex(JS, r"sessionHistory\.push\([^)]*(image|gradcam)")
        self.assertIn('id="sessionChart"', HTML)
        self.assertIn("renderSessionChart", JS)
        self.assertRegex(JS, r"sessionHistory\.map\([^\n]+probability")

    def test_real_gradcam_comparison_has_no_synthetic_heatmap(self):
        self.assertIn('id="comparisonSlider"', HTML)
        self.assertIn('id="originalCompareImage"', HTML)
        self.assertIn('id="gradcamCompareImage"', HTML)
        self.assertIn("clipPath", JS)
        self.assertNotIn("radial-gradient", JS)
        self.assertIn("CAM (cloud) or Grad-CAM (local)", HTML)

    def test_mobile_camera_capture_has_explicit_controls_and_medical_boundary(self):
        for element_id in (
            "openCameraButton",
            "cameraPanel",
            "cameraVideo",
            "capturePhotoButton",
            "switchCameraButton",
            "closeCameraButton",
            "cameraCanvas",
            "cameraStatus",
            "fundusEquipmentCheck",
            "cameraQualificationNotice",
        ):
            self.assertIn(f'id="{element_id}"', HTML)
        self.assertRegex(HTML, r'id="cameraVideo"[^>]+playsinline[^>]+muted')
        self.assertRegex(HTML, r"กล้องมือถือเปล่า\s*ๆ[^<]+ไม่ใช่[^<]+fundus")
        self.assertRegex(HTML, r"เลนส์|อะแดปเตอร์|adapter")

    def test_camera_uses_secure_browser_media_and_releases_hardware(self):
        self.assertIn("window.isSecureContext", JS)
        self.assertIn("navigator.mediaDevices.getUserMedia", JS)
        self.assertRegex(JS, r"facingMode:\s*\{ideal:\s*cameraFacingMode\}")
        self.assertIn("getTracks().forEach((track) => track.stop())", JS)
        self.assertIn("document.addEventListener('visibilitychange'", JS)
        self.assertIn("window.addEventListener('pagehide'", JS)
        self.assertNotRegex(JS, r"(?:torch|flash)\s*:\s*(?:true|\{)")

    def test_captured_frame_reuses_the_existing_private_file_flow(self):
        self.assertIn("cameraCanvas.toBlob", JS)
        self.assertIn("selectFile(capturedFile)", JS)
        self.assertIn("image/jpeg", JS)
        self.assertNotRegex(JS, r"localStorage\.setItem\([^,]+,\s*(?:selectedFile|capturedFile)")
        self.assertNotIn("sessionStorage", JS)

    def test_bare_phone_capture_cannot_reach_the_research_model(self):
        self.assertIn("selectedCaptureHasFundusOptics", JS)
        self.assertIn("fundusEquipmentCheck.checked", JS)
        self.assertRegex(
            JS,
            r"selectedInputSource === 'camera'\s*&&\s*!selectedCaptureHasFundusOptics",
        )
        self.assertRegex(
            HTML,
            r'id="fundusEquipmentCheck"[^>]+type="checkbox"',
        )

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

    def test_model_api_probe_accepts_same_origin_local_or_cloud_server(self):
        self.assertIn("fetch('/health'", JS)
        self.assertIn("cloud-research-model", JS)
        self.assertIn("fetch('/predict'", JS)

    def test_model_server_defaults_to_loopback_and_remains_single_request(self):
        server = (ROOT / "scripts" / "serve_retinova.py").read_text(encoding="utf-8")
        self.assertIn('default="127.0.0.1"', server)
        self.assertIn("HTTPServer((args.host, args.port)", server)
        self.assertNotIn("ThreadingHTTPServer", server)

    def test_render_blueprint_runs_the_real_onnx_model_on_free_plan(self):
        blueprint = (ROOT / "render.yaml").read_text(encoding="utf-8")
        self.assertIn("runtime: python", blueprint)
        self.assertIn("region: singapore", blueprint)
        self.assertIn("plan: free", blueprint)
        self.assertIn("healthCheckPath: /health", blueprint)
        self.assertIn("autoDeployTrigger: off", blueprint)
        self.assertIn("RETINOVA_TEAM_PASSCODE", blueprint)
        self.assertIn("sync: false", blueprint)
        self.assertIn("retinova_efficientnet_b0_cam.onnx", blueprint)
        self.assertNotIn("pip install torch", blueprint)

    def test_server_contract_uses_environment_and_documented_port(self):
        self.assertIn('os.environ.get("ROBOFLOW_API_KEY")', SERVER)
        self.assertIn('int(os.environ.get("PORT", "8000"))', SERVER)

    def test_pages_workflow_publishes_only_dashboard(self):
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
        self.assertIn("actions/deploy-pages@v4", workflow)
        self.assertRegex(workflow, r"path:\s*['\"]?dashboard")


if __name__ == "__main__":
    unittest.main()
