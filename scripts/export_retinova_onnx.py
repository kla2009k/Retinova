"""Export the deployed Retinova checkpoint to a lightweight ONNX CAM model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from retinova_ml.model import build_model


class EfficientNetCAMExport(nn.Module):
    def __init__(self, model: nn.Module):
        super().__init__()
        self.features = model.features
        self.avgpool = model.avgpool
        self.classifier = model.classifier

    def forward(self, inputs: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        features = self.features(inputs)
        pooled = self.avgpool(features)
        logits = self.classifier(torch.flatten(pooled, 1))
        weights = self.classifier[1].weight[:, :, None, None]
        cams = F.conv2d(features, weights)
        return logits, cams


def export_model(checkpoint_path: Path, output_path: Path, metadata_path: Path) -> None:
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    architecture = checkpoint.get("architecture", "efficientnet_b0")
    if architecture != "efficientnet_b0":
        raise ValueError("this exporter currently supports efficientnet_b0 checkpoints only")

    class_names = list(checkpoint["class_names"])
    image_size = int(checkpoint["image_size"])
    model = build_model(architecture, len(class_names), pretrained=False)
    model.load_state_dict(checkpoint["state_dict"])
    wrapper = EfficientNetCAMExport(model.eval()).eval()
    example = torch.zeros((1, 3, image_size, image_size), dtype=torch.float32)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        wrapper,
        (example,),
        output_path,
        input_names=["image"],
        output_names=["logits", "cams"],
        opset_version=18,
        dynamo=False,
    )

    preprocessing = checkpoint.get("preprocessing", {})
    metadata = {
        "architecture": architecture,
        "class_names": class_names,
        "image_size": image_size,
        "interpolation": preprocessing.get(
            "interpolation", checkpoint.get("config", {}).get("interpolation", "bilinear")
        ),
        "model_revision": checkpoint.get("git_revision", "unknown"),
        "target_layer": "features.8",
        "attribution_method": "class_activation_mapping",
    }
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=True, indent=2) + "\n", encoding="utf-8"
    )
    verify_export(wrapper, output_path, image_size)


def verify_export(wrapper: nn.Module, output_path: Path, image_size: int) -> None:
    import onnxruntime as ort

    # A smooth deterministic image is representative of camera input. Pixel-wise
    # random noise can amplify tiny backend convolution differences unrealistically.
    axis = torch.linspace(0.0, 1.0, image_size)
    horizontal = axis[None, :].expand(image_size, image_size)
    vertical = axis[:, None].expand(image_size, image_size)
    sample = torch.stack((horizontal, vertical, (horizontal + vertical) / 2.0))[None]
    wrapper.eval()
    with torch.inference_mode():
        expected_logits, expected_cams = wrapper(sample)

    session = ort.InferenceSession(str(output_path), providers=["CPUExecutionProvider"])
    actual_logits, actual_cams = session.run(None, {"image": sample.numpy()})
    logits_error = float(np.max(np.abs(actual_logits - expected_logits.numpy())))
    cams_error = float(np.max(np.abs(actual_cams - expected_cams.numpy())))
    if int(actual_logits.argmax(1)[0]) != int(expected_logits.argmax(1)[0]):
        raise RuntimeError("ONNX export changed the predicted class")
    if logits_error > 1e-3 or cams_error > 1e-3:
        raise RuntimeError(
            f"ONNX parity check failed: logits={logits_error:.3g}, cams={cams_error:.3g}"
        )
    print(
        f"ONNX parity passed: logits max error={logits_error:.3g}, "
        f"CAM max error={cams_error:.3g}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    args = parser.parse_args()
    export_model(args.checkpoint, args.output, args.metadata)


if __name__ == "__main__":
    main()
