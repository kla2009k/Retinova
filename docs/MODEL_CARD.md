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

The implemented method is class-specific Grad-CAM from the final convolutional feature block of the same checkpoint used for prediction. EfficientNet-B0 uses `features.8`; ResNet-18 uses `layer4.1.conv2`. It is an attribution map, not a lesion segmentation or causal explanation.

## Known risks

- Class imbalance, especially Hypertension.
- Dataset/domain shift across cameras, clinics, demographics, and image quality.
- Simplification from bilateral multi-label data to a single-image label.
- Shortcut learning from borders, illumination, acquisition devices, or annotations.
- Over-trust in probability values and visual explanations.

## Current patient-grouped baseline

EfficientNet-B0 was selected over ResNet-18 using validation macro F1 (0.577 versus 0.552). On 957 held-out images from 503 patients, the selected candidate achieved:

- Macro F1: 0.581 (patient-bootstrap 95% interval 0.525–0.622)
- Balanced accuracy: 0.642 (patient-bootstrap 95% interval 0.579–0.689)
- Weakest recall: Other 0.340 and Hypertension 0.389
- Patient overlap across train/validation/test: 0

The ResNet-18 comparator reached test macro F1 0.562 and balanced accuracy 0.617. See [Baseline Evaluation v1](EVALUATION_BASELINE_V1.md). These values are development evidence, not a clinical performance claim. Both checkpoints are withheld pending dataset and derived-weight licensing clarification.
