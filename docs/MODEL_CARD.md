# Retinova Model Card

Status: **baseline trained — no production checkpoint approved**
Last updated: 2026-08-01

## Intended task

Single retinal fundus image classification into eight mutually exclusive research labels: Normal, Diabetes, Glaucoma, Cataract, AMD, Hypertension, Myopia, and Other.

## Intended use

Education, research, supervised demonstrations, and development of a screening workflow. The system must not be used as a diagnosis or as the sole basis for patient care.

## Data

Local ODIR-derived data. The audited label table contains 6,392 image rows. The original ODIR framing is patient-level, bilateral, and multi-label; Retinova's current reduced task is image-level, single-label. This mismatch is a known limitation.

## Evaluation policy

- Split by patient identifier.
- Select checkpoints using validation macro F1.
- Keep the test group untouched until the pipeline is frozen.
- Report macro F1, balanced accuracy, per-class sensitivity/specificity, confusion matrix, calibration, and patient-bootstrap confidence intervals.
- Do not publish a headline performance figure until the test artifact is reproducible.

## Explainability

The planned method is class-specific Grad-CAM from the final convolutional block of the same checkpoint used for prediction. It is an attribution map, not a lesion segmentation or causal explanation.

## Known risks

- Class imbalance, especially Hypertension.
- Dataset/domain shift across cameras, clinics, demographics, and image quality.
- Simplification from bilateral multi-label data to a single-image label.
- Shortcut learning from borders, illumination, acquisition devices, or annotations.
- Over-trust in probability values and visual explanations.

## Current patient-grouped baseline

ResNet-18 baseline v1 on 957 held-out images from 503 patients:

- Macro F1: 0.562 (patient-bootstrap 95% interval 0.507–0.603)
- Balanced accuracy: 0.617 (patient-bootstrap 95% interval 0.555–0.667)
- Weakest recall: Other 0.264 and Hypertension 0.444
- Patient overlap across train/validation/test: 0

See [Baseline Evaluation v1](EVALUATION_BASELINE_V1.md). These values are development evidence, not a clinical performance claim. The checkpoint is withheld pending dataset and derived-weight licensing clarification.
