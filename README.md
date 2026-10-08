# Retinova

Retinova is a research prototype for screening **retinal fundus photographs**. It is not an iris-identification system and it is not a medical diagnosis.

## Public preview

- Website: https://kla2009k.github.io/Retinova/
- Current mode: static preview with local image-readiness checks; real inference requires the separate ONNX server
- Live disease inference: GitHub Pages remains a static preview; the optional Render service runs the real checkpoint behind Team Login
- Attribution: class-specific Grad-CAM is available in the local PyTorch server; the authenticated Render ONNX server returns class-specific CAM from the same selected checkpoint
- Welcome page: Guest access is public; Team Login is enabled by the optional localhost or authenticated Render server
- Session results: no fabricated patient records; only real local results are held in page memory and disappear on refresh
- Mobile camera: live rear/front camera capture on HTTPS/localhost; bare-phone external-eye captures are blocked from model inference

The public preview deliberately does not display invented accuracy, medical findings, or synthetic heatmaps.

![QR code for the Retinova public preview](docs/retinova-qr.png)

## Run locally

```powershell
python -m pip install -r requirements.txt
cd dashboard
python serve_with_log.py
```

Open `http://127.0.0.1:8000`.

Optional legacy Roboflow inference must stay server-side:

```powershell
$env:ROBOFLOW_API_KEY="your-rotated-key"
python serve_with_log.py
```

Never add the key to `dashboard/app.js` or commit `.env`.

## Documentation

- [Thai training-to-usage guide](docs/TRAINING_AND_USAGE_GUIDE_TH.md)
- [Thai live-camera and current model guide](docs/CAMERA_AND_MODEL_USAGE_TH.md)
- [Thai poster UI and demonstration guide](docs/POSTER_UI_GUIDE_TH.md)
- [Thai team presentation script and judge Q&A](docs/TEAM_PRESENTATION_SCRIPT_TH.md)
- [Model card](docs/MODEL_CARD.md)
- [Patient-grouped baseline evaluation](docs/EVALUATION_BASELINE_V1.md)
- [Privacy and safety](docs/PRIVACY.md)
- [Product specification](docs/RETINOVA_SPEC.md)
- [Implementation plan](docs/IMPLEMENTATION_PLAN.md)

## Current dataset audit

The local ODIR-derived table contains 6,392 per-image rows across eight mutually exclusive labels. The existing 2,103-image Roboflow subset was randomly split per image, so patients with two eyes can leak across splits. All new evaluation must therefore split by patient identifier before model selection.

| Label | Images |
|---|---:|
| Normal | 2,873 |
| Diabetes | 1,608 |
| Other | 708 |
| Cataract | 293 |
| Glaucoma | 284 |
| AMD | 266 |
| Myopia | 232 |
| Hypertension | 128 |

These are dataset counts, not claims about model accuracy.

## Reproduce the baseline

```powershell
python -m scripts.build_retinova_manifest
python -m scripts.train_retinova --config configs/train_efficientnet_b0.json
python -m scripts.evaluate_retinova `
  --checkpoint models/efficientnet_b0_patient_grouped_v1/retinova_efficientnet_b0_best.pt
python -m scripts.gradcam_retinova `
  --checkpoint models/efficientnet_b0_patient_grouped_v1/retinova_efficientnet_b0_best.pt `
  --image path/to/fundus.jpg
```

EfficientNet-B0 was selected over ResNet-18 by validation macro F1 (0.577 versus 0.552), before comparing held-out test results. Its test macro F1 is 0.581 and balanced accuracy is 0.642. See the evaluation report for patient-bootstrap intervals, the controlled comparison, and class-level failures. On 2026-08-18, the project owner confirmed the right to publish and deploy the selected research-demo checkpoint. ODIR images are still not redistributed.

## Run the real local model + Grad-CAM web mode

After training (or with the local checkpoint created in this workspace):

```powershell
python -m scripts.serve_retinova `
  --checkpoint models/efficientnet_b0_patient_grouped_v1/retinova_efficientnet_b0_best.pt
```

Open `http://127.0.0.1:8000`. On localhost only, the page detects `/health`; the analysis button then calls the local checkpoint and returns probabilities plus class-specific Grad-CAM. The server binds to loopback, does not log images, and is not the public GitHub Pages deployment.

### Optional Team Login for the local model

Set a passcode only in the terminal process that starts the server:

```powershell
$env:RETINOVA_TEAM_PASSCODE="replace-with-a-long-random-passcode"
python -m scripts.serve_retinova `
  --checkpoint models/efficientnet_b0_patient_grouped_v1/retinova_efficientnet_b0_best.pt
Remove-Item Env:RETINOVA_TEAM_PASSCODE
```

The passcode is compared server-side and is never written to browser storage. A successful login receives an in-memory, eight-hour `HttpOnly; SameSite=Strict` localhost cookie. `/predict` returns HTTP 401 without that session. Logging out deletes the server session and cookie. If `RETINOVA_TEAM_PASSCODE` is unset, the loopback server remains in open-local demonstration mode.

This is a team demonstration gate, not a production identity system or medical-record login. It has no user accounts, password reset, database, audit trail, TLS termination, or role-based authorization. Do not expose this development server to a network.

## Deploy the authenticated research demo on Render

The repository-root `render.yaml` defines one Singapore-region Free web service. Render prompts for `RETINOVA_TEAM_PASSCODE`; use a unique value of at least 12 characters. The service loads the versioned EfficientNet-B0 ONNX checkpoint from the repository and serves the UI, prediction API, and class activation map from one HTTPS origin. The existing service URL is https://retinova-f70k.onrender.com/ and its `/health` endpoint reports `cloud-research-model` with Team Login required. GitHub Pages remains a separate static preview.

Automatic service deploys are disabled in the Blueprint. Also set the Blueprint's **Auto Sync** setting to **No** after creation so future YAML edits cannot change paid resources without a manual review. See the [Thai Render deployment and three-day cost guide](docs/RENDER_DEPLOYMENT_TH.md).

### Live phone camera

The analysis page uses the standard browser `getUserMedia()` API, preferring the rear camera, without audio or automatic illumination. It captures a JPEG in page memory and reuses the existing file-validation path. Camera tracks stop when the panel closes, the view changes, the tab is hidden, or the page exits.

A bare smartphone camera does not produce the retinal fundus photographs used for model training. Captures without an explicit fundus-adapter/condensing-lens acknowledgement may be inspected for file properties but are blocked from local inference. See the camera guide for the hardware boundary, privacy flow, and phone-to-model deployment options.

### Truthful replacements for unsupported legacy UI

- `94.2% accuracy` → measured patient-grouped test macro F1 0.581 and balanced accuracy 0.642, each with a 95% confidence interval.
- Fake patient history → session-only real inference summaries; no names, identifiers, filenames, images, or Grad-CAM data are stored.
- `Eye Health Score` → predicted-class probability, explicitly labelled as a model probability and not a health score.
- Synthetic heatmap → a comparison slider using the original selected image and the real class-specific Grad-CAM returned by the same checkpoint.

## License and intended use

The repository currently has no clinical-use license or regulatory approval. Use it for education, research, and supervised demonstrations only. Dataset use remains subject to the original dataset terms.

## 2026-10-08 development status

The ONNX endpoint now rejects unsupported formats, over-24-megapixel files, and near-uniform blank images before inference. This is a technical upload gate, not a validated retinal image-quality model. The public preview and model-service status, deployment attempt, verification evidence, and next development priorities are recorded in [the Thai release note](docs/RETINOVA_NEXT_PHASE_2026_10_08_TH.md).
