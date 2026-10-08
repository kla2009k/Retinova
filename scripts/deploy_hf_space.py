"""Publish the Retinova ONNX research demo to a password-gated HF Docker Space."""

from pathlib import Path
import secrets
import shutil
import tempfile

from huggingface_hub import HfApi


ROOT = Path(__file__).resolve().parents[1]
REPO_ID = "NemophilaNah/Retinova-Research"
MODEL_DIR = "models/efficientnet_b0_patient_grouped_v1"
SECRET_FILE = ROOT / ".env.retinova-hf"

SPACE_README = """---
title: Retinova Research
emoji: 👁️
colorFrom: blue
colorTo: cyan
sdk: docker
app_port: 7860
---

Retinova is a research demonstration for retinal fundus images. Team Login is
required for inference. Outputs are not diagnoses or validated for patient care.
The ONNX checkpoint and web application are sourced from the project owner.
"""

DOCKERFILE = """FROM python:3.11-slim
WORKDIR /app
COPY requirements-render.txt .
RUN pip install --no-cache-dir -r requirements-render.txt
COPY dashboard/ dashboard/
COPY retinova_ml/ retinova_ml/
COPY scripts/ scripts/
COPY models/ models/
ENV PORT=7860 PYTHONDONTWRITEBYTECODE=1
EXPOSE 7860
CMD ["python", "-m", "scripts.serve_retinova", "--onnx-model", "models/efficientnet_b0_patient_grouped_v1/retinova_efficientnet_b0_cam.onnx", "--metadata", "models/efficientnet_b0_patient_grouped_v1/retinova_efficientnet_b0_cam.json", "--host", "0.0.0.0", "--deployment-mode", "cloud"]
"""


def main() -> None:
    api = HfApi()
    if not SECRET_FILE.exists():
        SECRET_FILE.write_text("RETINOVA_TEAM_PASSCODE=" + secrets.token_urlsafe(24) + "\n", encoding="utf-8")
    passcode = SECRET_FILE.read_text(encoding="utf-8").split("=", 1)[1].strip()
    if len(passcode) < 12:
        raise ValueError("team passcode must have at least 12 characters")

    with tempfile.TemporaryDirectory(prefix="retinova-space-") as temporary:
        stage = Path(temporary)
        (stage / "README.md").write_text(SPACE_README, encoding="utf-8")
        (stage / "Dockerfile").write_text(DOCKERFILE, encoding="utf-8")
        shutil.copy2(ROOT / "requirements-render.txt", stage / "requirements-render.txt")
        for relative in (
            "dashboard/index.html", "dashboard/app.js", "dashboard/styles.css",
            "dashboard/assets/anatomy.jpg", "dashboard/assets/fundus-pair.jpg",
            "retinova_ml/__init__.py", "retinova_ml/onnx_inference.py",
            "scripts/serve_retinova.py",
            f"{MODEL_DIR}/retinova_efficientnet_b0_cam.onnx",
            f"{MODEL_DIR}/retinova_efficientnet_b0_cam.json",
        ):
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)
        api.create_repo(REPO_ID, repo_type="space", space_sdk="docker", exist_ok=True)
        api.add_space_secret(REPO_ID, "RETINOVA_TEAM_PASSCODE", passcode)
        result = api.upload_folder(
            repo_id=REPO_ID,
            repo_type="space",
            folder_path=str(stage),
            commit_message="Deploy Retinova ONNX research demo",
        )
    print(f"Space: https://huggingface.co/spaces/{REPO_ID}")
    print(f"Commit: {result}")
    print(f"Team passcode saved locally: {SECRET_FILE}")


if __name__ == "__main__":
    main()
