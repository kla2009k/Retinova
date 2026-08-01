# Spec: Retinova Competition Release

## Objective

Build and publish a truthful, bilingual retinal fundus screening web application under the Retinova name. The first public release must be safe to share immediately. The complete release adds a reproducible patient-level training and evaluation pipeline plus real Grad-CAM generated from a model we control.

Retinova analyzes retinal fundus photographs. It does not analyze the iris and does not perform identity recognition.

## Release Strategy

### Release 1 — Public Preview

- Static GitHub Pages deployment at `https://kla2009k.github.io/Retinova/`.
- Upload and education flow that works without exposing an API key.
- Clearly labelled demo result when no live model backend is configured.
- No invented accuracy, encryption, Grad-CAM, lesion, or diagnostic claims.
- Team documentation and QR code.

### Release 2 — Real AI

- Patient-grouped train/validation/test split.
- Reproducible PyTorch training and evaluation.
- Versioned checkpoint and metric artifacts.
- Real class-specific Grad-CAM generated from the same model prediction.
- Backend endpoint returning prediction, calibrated probability, model version, quality status, and heatmap provenance.

## Tech Stack

- Public frontend: semantic HTML, CSS, and vanilla JavaScript.
- Charts: vendored Chart.js.
- Local/API backend: Python 3.11+.
- Model target: PyTorch with an ImageNet-pretrained convolutional backbone.
- Explainability: Grad-CAM calculated from the selected class and final convolutional feature layer.
- Static hosting: GitHub Pages through GitHub Actions.

## Commands

- Local preview: `python dashboard/serve_with_log.py`
- Python tests: `python -m unittest discover -s tests -v`
- JavaScript syntax: `node --check dashboard/app.js`
- Data audit: `python scripts/audit_dataset.py`
- Train: `python scripts/train_retinova.py --config configs/train.yaml`
- Evaluate: `python scripts/evaluate_retinova.py --checkpoint models/retinova_best.pth`
- Grad-CAM smoke test: `python scripts/gradcam_retinova.py --checkpoint models/retinova_best.pth --image <path>`

Commands for Release 2 are acceptance targets and will be added incrementally.

## Project Structure

- `dashboard/` — deployed frontend and local inference proxy.
- `scripts/` — data preparation, training, evaluation, and inference utilities.
- `tests/` — unit and integration tests.
- `docs/` — architecture, model card, training guide, team guide, and deployment notes.
- `configs/` — versioned training configuration without secrets or machine-specific paths.
- `models/` and `artifacts/` — local generated outputs; ignored by Git.
- `archive_4/` — local ODIR data; ignored by Git.

## Code Style

- Pure transformation logic is separated from DOM and network code so it can be tested.
- External data is validated before use.
- UI copy explicitly identifies evidence provenance.
- Python uses `pathlib`, type hints for public functions, and configuration relative to the repository.

## Testing Strategy

- Unit tests for prediction mapping, risk policy, input validation, grouped splitting, and Grad-CAM output shape.
- Integration tests for the local health and prediction endpoints using a fake model adapter.
- Static checks for missing assets, duplicate IDs, secrets, and unsafe public claims.
- Browser smoke tests for upload, keyboard navigation, responsive layouts, and console/network errors when a browser is available.

## Boundaries

- Always: split data by patient, retain both eyes in one split, version metrics, validate image type/size, and label non-model output.
- Ask first: add a third-party service, publish a checkpoint with unclear licensing, collect user health data, or add real authentication.
- Never: commit secrets or patient images, claim diagnosis, fabricate heatmaps/metrics, or silently replace an API failure with a realistic-looking medical result.

## Success Criteria

- GitHub Pages URL returns HTTP 200 and the QR code resolves to it.
- Public source contains no API key or plaintext-password authentication.
- Public pages use Retinova consistently and describe retinal fundus screening accurately.
- The team guide explains dataset preparation, model training, evaluation, Grad-CAM, deployment, and use.
- Release 2 metrics are generated from a patient-grouped held-out test set.
- Every displayed heatmap is calculated from the same model and class as the displayed prediction.

## Open Questions

- Final competition acceptance and submission requirements must be confirmed with the school.
- Publishing the trained checkpoint depends on dataset and model-weight licensing review.
- The production inference host must be chosen before live public inference can replace demo mode.
