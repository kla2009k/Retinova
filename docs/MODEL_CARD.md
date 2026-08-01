# Retinova Model Card

Status: **development — no production checkpoint approved**
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

## Current metrics

None approved. Any legacy dashboard values or provider-side metrics are excluded until reproduced with the patient-grouped test policy.
