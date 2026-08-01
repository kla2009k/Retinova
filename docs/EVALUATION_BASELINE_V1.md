# Retinova Patient-Grouped Baseline Evaluation v1

Status: **research baseline; not for clinical use**

Evaluation date: 2026-08-01

Task: single-fundus-image, single-label, eight-class classification

## Selection decision

Two ImageNet-initialized candidates were trained on the same frozen patient-grouped manifest. Checkpoints were selected inside each run by validation macro F1. EfficientNet-B0 was then selected as the Retinova research baseline because its best validation macro F1 was higher.

| Candidate | Best validation macro F1 | Test macro F1 | Test balanced accuracy | Decision |
|---|---:|---:|---:|---|
| ResNet-18 | 0.552 | 0.562 | 0.617 | comparator retained locally |
| EfficientNet-B0 | **0.577** | **0.581** | **0.642** | selected research baseline |

The selection rule uses validation, not test performance. Test results are reported once as final evidence and must not be used for further tuning.

## Reproducibility identity

- Canonical manifest SHA-256: `7b0b734ac2c54b0296e92894a50120388d46b32fdfd83ce5e4b9f9d5534f8d60`
- Selected checkpoint SHA-256: `49e408b205e84443f150f08d9095766d4b82edc57534544498116e29d54fb098`
- Architecture: EfficientNet-B0
- Input: RGB, resize short side to 256 with bicubic interpolation, center crop 224×224
- Normalization: ImageNet mean `(0.485, 0.456, 0.406)` and standard deviation `(0.229, 0.224, 0.225)`
- Optimizer: AdamW, learning rate 0.0003, weight decay 0.0001
- Loss: weighted cross-entropy computed from training-split class counts
- Schedule: cosine annealing, maximum 8 epochs, early-stopping patience 3
- Random seed: 42
- Model revision recorded at training: `0132f70dbfffa6c0e34de0319260051683619dcb`

## Split integrity

The 6,392-image ODIR-derived table was split with `StratifiedGroupKFold` using patient ID as the group. No patient occurs in more than one split.

| Split | Images | Patients |
|---|---:|---:|
| Train | 4,477 | 2,352 |
| Validation | 958 | 503 |
| Test | 957 | 503 |

Patient overlap across splits: **0**.

## Selected model test results

| Metric | Point estimate | Patient-bootstrap 95% interval |
|---|---:|---:|
| Macro F1 | 0.581 | 0.525–0.622 |
| Balanced accuracy | 0.642 | 0.579–0.689 |

Confidence intervals use 500 bootstrap resamples of patients, not individual images. The selected checkpoint came from epoch 7 with validation macro F1 0.577.

## Per-class results

| Class | Recall / sensitivity | Specificity |
|---|---:|---:|
| Normal (N) | 0.615 | 0.800 |
| Diabetes (D) | 0.617 | 0.840 |
| Glaucoma (G) | 0.667 | 0.957 |
| Cataract (C) | 0.909 | 0.975 |
| AMD (A) | 0.659 | 0.969 |
| Hypertension (H) | 0.389 | 0.983 |
| Myopia (M) | 0.943 | 0.987 |
| Other (O) | 0.340 | 0.959 |

The weak H and O recall values are especially important: a high specificity does not compensate for missed positives in a screening setting.

## Confusion matrix

Rows are true classes and columns are predicted classes, ordered N, D, G, C, A, H, M, O.

```text
          Predicted
True      N    D   G   C   A   H   M   O
N       265   88  22  10  14   6   6  20
D        54  148  12   3   4   9   1   9
G        10    2  28   2   0   0   0   0
C         3    0   0  40   0   0   0   1
A         5    3   0   0  27   0   2   4
H         5    3   0   0   2   7   0   1
M         1    0   0   0   1   0  33   0
O        27   19   5   8   7   1   3  36
```

## Grad-CAM verification

The same EfficientNet-B0 checkpoint used for prediction generates class-specific Grad-CAM from `features.8`. Automated tests verify output shape and range, and verify that changing the target class changes the attribution.

In one glaucoma-labelled test example, a Grad-CAM explicitly targeted to G emphasized the optic-disc region, but the model predicted Normal with probability 0.610 and assigned G only 0.131. This is a useful counterexample: plausible-looking attribution does not prove that a prediction is correct, clinically grounded, or causal.

The test image, generated overlay, and checkpoint are not published because ODIR redistribution and derived-weight licensing have not been confirmed.

## What improved and what did not

Compared with ResNet-18, EfficientNet-B0 improved test macro F1 by 0.019 and balanced accuracy by 0.025. Recall improved for N, D, G, C, and O; A and M were unchanged to rounding; H recall fell from 0.444 to 0.389. The confidence intervals overlap, so this small internal comparison does not establish broad superiority.

Calibration, external-site performance, image-quality rejection, demographic subgroup performance, and clinical utility are still unmeasured.

## Decision

EfficientNet-B0 becomes the **selected internal research baseline**, but it is **not approved for public inference or clinical use**. Next work should prioritize:

1. Resolve dataset and derived-weight licensing.
2. Review the single-image target derivation against original bilateral labels.
3. Add image-quality and out-of-domain rejection.
4. Improve H and O recall without sacrificing calibration.
5. Measure probability calibration and define abstention thresholds on validation data.
6. Validate on an independent external dataset/site.
7. Obtain ophthalmologist review of errors and Grad-CAM patterns.
