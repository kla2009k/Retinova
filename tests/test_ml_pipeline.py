import unittest

import numpy as np
import pandas as pd
import torch
from torch import nn

from retinova_ml.data import assign_grouped_splits, manifest_fingerprint
from retinova_ml.gradcam import GradCAM
from retinova_ml.model import build_model, gradcam_target
from retinova_ml.training import bootstrap_patient_metrics, build_transform, compute_metrics


class GroupedSplitTests(unittest.TestCase):
    def setUp(self):
        rows = []
        for patient in range(120):
            label = patient % 3
            for eye in ("left", "right"):
                rows.append({"patient_id": patient, "label": label, "filename": f"{patient}_{eye}.jpg"})
        self.frame = pd.DataFrame(rows)

    def test_split_is_patient_disjoint_and_deterministic(self):
        first = assign_grouped_splits(self.frame, "patient_id", "label", seed=17)
        second = assign_grouped_splits(self.frame, "patient_id", "label", seed=17)
        self.assertListEqual(first["split"].tolist(), second["split"].tolist())
        patient_split_counts = first.groupby("patient_id")["split"].nunique()
        self.assertEqual(1, patient_split_counts.max())
        self.assertSetEqual({"train", "val", "test"}, set(first["split"]))

    def test_each_split_retains_all_labels(self):
        result = assign_grouped_splits(self.frame, "patient_id", "label", seed=3)
        for split in ("train", "val", "test"):
            self.assertSetEqual({0, 1, 2}, set(result.loc[result["split"] == split, "label"]))

    def test_manifest_fingerprint_ignores_machine_specific_image_path(self):
        manifest = assign_grouped_splits(self.frame, "patient_id", "label", seed=3)
        manifest["label_index"] = manifest["label"]
        manifest["image_path"] = "C:/machine-one/image.jpg"
        first = manifest_fingerprint(manifest)
        manifest["image_path"] = "D:/machine-two/image.jpg"
        self.assertEqual(first, manifest_fingerprint(manifest))


class TinyClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 4, kernel_size=3, padding=1, bias=False),
            nn.ReLU(),
            nn.Conv2d(4, 5, kernel_size=3, padding=1, bias=False),
            nn.ReLU(),
        )
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Linear(5, 3, bias=False)

    def forward(self, inputs):
        features = self.features(inputs)
        return self.classifier(self.pool(features).flatten(1))


class GradCAMTests(unittest.TestCase):
    def test_supported_backbones_expose_logits_and_gradcam_layer(self):
        for architecture in ("resnet18", "efficientnet_b0"):
            model = build_model(architecture, num_classes=8, pretrained=False).eval()
            with torch.no_grad():
                logits = model(torch.randn(1, 3, 64, 64))
            layer, layer_name = gradcam_target(model, architecture)
            self.assertEqual((1, 8), tuple(logits.shape))
            self.assertIsInstance(layer, nn.Module)
            self.assertTrue(layer_name)

    def test_unknown_backbone_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported architecture"):
            build_model("mystery_net", num_classes=8, pretrained=False)

    def test_cam_is_normalized_and_matches_input_size(self):
        torch.manual_seed(11)
        model = TinyClassifier().eval()
        inputs = torch.randn(2, 3, 16, 12)
        with GradCAM(model, model.features[2]) as explainer:
            heatmaps, logits = explainer(inputs, class_indices=torch.tensor([0, 1]))
        self.assertEqual((2, 1, 16, 12), tuple(heatmaps.shape))
        self.assertEqual((2, 3), tuple(logits.shape))
        self.assertTrue(torch.isfinite(heatmaps).all())
        self.assertGreaterEqual(float(heatmaps.min()), 0.0)
        self.assertLessEqual(float(heatmaps.max()), 1.0)

    def test_target_class_changes_attribution(self):
        torch.manual_seed(19)
        model = TinyClassifier().eval()
        inputs = torch.randn(1, 3, 10, 10)
        with GradCAM(model, model.features[2]) as explainer:
            class_zero, _ = explainer(inputs, class_indices=torch.tensor([0]))
            class_one, _ = explainer(inputs, class_indices=torch.tensor([1]))
        self.assertFalse(np.allclose(class_zero.numpy(), class_one.numpy()))


class EvaluationTests(unittest.TestCase):
    def test_transform_accepts_bicubic_and_rejects_unknown_interpolation(self):
        self.assertIsNotNone(build_transform(False, 224, interpolation="bicubic"))
        with self.assertRaisesRegex(ValueError, "unsupported interpolation"):
            build_transform(False, 224, interpolation="nearestish")

    def test_metrics_include_per_class_specificity(self):
        metrics = compute_metrics([0, 0, 1, 1], [0, 1, 1, 1], class_names=["A", "B"])
        self.assertAlmostEqual(1.0, metrics["per_class_specificity"]["A"])
        self.assertAlmostEqual(0.5, metrics["per_class_specificity"]["B"])

    def test_patient_bootstrap_is_deterministic(self):
        labels = np.array([0, 0, 1, 1, 0, 1])
        predictions = np.array([0, 1, 1, 1, 0, 0])
        patients = np.array([10, 10, 20, 20, 30, 30])
        first = bootstrap_patient_metrics(
            labels, predictions, patients, iterations=40, seed=9, class_names=["A", "B"]
        )
        second = bootstrap_patient_metrics(
            labels, predictions, patients, iterations=40, seed=9, class_names=["A", "B"]
        )
        self.assertEqual(first, second)
        self.assertIn("macro_f1", first)


if __name__ == "__main__":
    unittest.main()
