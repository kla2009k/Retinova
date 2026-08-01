"""Generate a real class-specific Grad-CAM from a Retinova checkpoint."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
import torch

from retinova_ml.gradcam import GradCAM
from retinova_ml.model import build_model, gradcam_target
from retinova_ml.training import build_transform


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--target-class", type=int)
    parser.add_argument("--output", default="artifacts/gradcam_overlay.png")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    class_names = checkpoint["class_names"]
    architecture = checkpoint.get("architecture", "resnet18")
    model = build_model(architecture, len(class_names), pretrained=False).to(device)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    source = Image.open(args.image).convert("RGB")
    image_size = checkpoint["image_size"]
    interpolation = checkpoint.get("preprocessing", {}).get(
        "interpolation", checkpoint.get("config", {}).get("interpolation", "bilinear")
    )
    tensor = (
        build_transform(False, image_size, interpolation=interpolation)(source)
        .unsqueeze(0)
        .to(device)
    )
    target = None if args.target_class is None else torch.tensor([args.target_class], device=device)
    target_layer, target_layer_name = gradcam_target(model, architecture)
    with GradCAM(model, target_layer) as explainer:
        heatmaps, logits = explainer(tensor, class_indices=target)
    probabilities = logits.softmax(dim=1)[0]
    target_index = int(probabilities.argmax()) if target is None else args.target_class
    heatmap = (heatmaps[0, 0].numpy() * 255).astype(np.uint8)
    heat_image = Image.fromarray(heatmap, mode="L")
    color_heatmap = ImageOps.colorize(heat_image, black="#10233f", mid="#f5b942", white="#d92d20")
    base = source.resize(
        (int(source.width * 256 / min(source.size)), int(source.height * 256 / min(source.size))),
        Image.Resampling.BILINEAR,
    )
    left = (base.width - image_size) // 2
    top = (base.height - image_size) // 2
    base = base.crop((left, top, left + image_size, top + image_size))
    overlay = Image.blend(base, color_heatmap, alpha=0.42)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(output)
    provenance = {
        "output": str(output),
        "checkpoint": str(Path(args.checkpoint).resolve()),
        "model_revision": checkpoint.get("git_revision", "unknown"),
        "target_class_index": target_index,
        "target_class": class_names[target_index],
        "target_layer": target_layer_name,
        "predicted_class": class_names[int(probabilities.argmax())],
        "probabilities": {
            name: float(probability) for name, probability in zip(class_names, probabilities, strict=True)
        },
        "interpretation": "model attribution, not lesion segmentation",
    }
    output.with_suffix(".json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
