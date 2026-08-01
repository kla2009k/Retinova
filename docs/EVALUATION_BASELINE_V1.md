# Retinova Baseline Evaluation v1

Status: research baseline; not for clinical use

Evaluation date: 2026-08-01

Architecture: ResNet-18, ImageNet-initialized, 224×224 input

Task: single-fundus-image, single-label, eight-class classification

- Canonical manifest SHA-256: `7b0b734ac2c54b0296e92894a50120388d46b32fdfd83ce5e4b9f9d5534f8d60`
- Local checkpoint SHA-256: `12df77ed3576946ba04793c7c4928aafa165f185c1d85a9e1197fc5609cc9a2a`

## Split integrity

The 6,392-image ODIR-derived table was split with `StratifiedGroupKFold` using patient ID as the group. No patient occurs in more than one split.

| Split | Images | Patients |
|---|---:|---:|
| Train | 4,477 | 2,352 |
| Validation | 958 | 503 |
| Test | 957 | 503 |

Patient overlap across splits: **0**.

## Headline test results

| Metric | Point estimate | Patient-bootstrap 95% interval |
|---|---:|---:|
| Macro F1 | 0.562 | 0.507–0.603 |
| Balanced accuracy | 0.617 | 0.555–0.667 |

Confidence intervals use 500 bootstrap resamples of patients, not individual images. The best validation macro F1 used for checkpoint selection was 0.552.

## Per-class results

| Class | Recall / sensitivity | Specificity |
|---|---:|---:|
| Normal (N) | 0.589 | 0.798 |
| Diabetes (D) | 0.575 | 0.838 |
| Glaucoma (G) | 0.619 | 0.961 |
| Cataract (C) | 0.841 | 0.982 |
| AMD (A) | 0.659 | 0.977 |
| Hypertension (H) | 0.444 | 0.979 |
| Myopia (M) | 0.943 | 0.986 |
| Other (O) | 0.264 | 0.908 |

## Confusion matrix

Rows are true classes and columns are predicted classes, ordered N, D, G, C, A, H, M, O.

```text
          Predicted
True      N    D   G   C   A   H   M   O
N       254   87  22   5  10   8   7  38
D        53  138  10   1   2   9   1  26
G        12    0  26   1   0   0   2   1
C         5    0   0  37   0   0   0   2
A         5    0   0   0  27   0   1   8
H         2    2   0   1   2   8   0   3
M         1    0   0   0   1   0  33   0
O        28   27   4   8   6   3   2  28
```

## Grad-CAM verification

The repository implementation computes gradients of a selected class score with respect to `layer4.1.conv2`, pools the gradients into channel weights, combines the activation maps, applies ReLU, resizes, and normalizes the result. Automated tests verify output shape/range and verify that changing the target class changes the attribution.

A local review on a misclassified glaucoma-labelled test image showed attribution on the retinal border/illumination rather than a trustworthy clinical structure. This is useful failure evidence and indicates shortcut learning. The image and checkpoint are not published because ODIR redistribution and derived-weight licensing have not been confirmed.

## Decision

This checkpoint is **not approved for public inference or clinical use**. Next work should prioritize:

1. Resolve dataset and derived-weight licensing.
2. Review the single-image target derivation against original bilateral labels.
3. Add image-quality and fundus-domain rejection.
4. Improve Other and Hypertension recall without sacrificing calibration.
5. Validate on an independent external dataset/site.
6. Perform ophthalmologist review of failure cases and Grad-CAM patterns.
