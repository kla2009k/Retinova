"""Local prediction and Grad-CAM adapter for the Retinova research UI."""
import base64
from io import BytesIO

import numpy as np
from PIL import Image, ImageOps
import torch

from .gradcam import GradCAM
from .model import build_resnet18, gradcam_target_layer
from .training import build_transform


class RetinovaPredictor:
    def __init__(self, checkpoint_path, device=None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
        self.class_names = self.checkpoint["class_names"]
        self.image_size = int(self.checkpoint["image_size"])
        self.model = build_resnet18(len(self.class_names), pretrained=False).to(self.device)
        self.model.load_state_dict(self.checkpoint["state_dict"])
        self.model.eval()

    def predict(self, image_bytes):
        with Image.open(BytesIO(image_bytes)) as encoded:
            source = encoded.convert("RGB")
        if min(source.size) < self.image_size:
            raise ValueError(f"image must be at least {self.image_size} px on its shortest side")
        ratio = source.width / source.height
        if ratio < 0.5 or ratio > 2.0:
            raise ValueError("image aspect ratio is outside the accepted range")
        tensor = build_transform(False, self.image_size)(source).unsqueeze(0).to(self.device)
        with GradCAM(self.model, gradcam_target_layer(self.model)) as explainer:
            heatmaps, logits = explainer(tensor)
        probabilities = logits.softmax(dim=1)[0]
        predicted_index = int(probabilities.argmax())
        overlay = self._overlay(source, heatmaps[0, 0].numpy())
        return {
            "prediction": self.class_names[predicted_index],
            "probability": float(probabilities[predicted_index]),
            "probabilities": {
                name: float(value)
                for name, value in zip(self.class_names, probabilities, strict=True)
            },
            "gradcam_data_url": overlay,
            "provenance": {
                "architecture": self.checkpoint["architecture"],
                "model_revision": self.checkpoint.get("git_revision", "unknown"),
                "target_class": self.class_names[predicted_index],
                "target_layer": "layer4.1.conv2",
                "interpretation": "model attribution, not lesion segmentation",
            },
            "warning": "research screening output; not a medical diagnosis",
        }

    def _overlay(self, source, heatmap):
        resized = source.resize(
            (
                int(source.width * 256 / min(source.size)),
                int(source.height * 256 / min(source.size)),
            ),
            Image.Resampling.BILINEAR,
        )
        left = (resized.width - self.image_size) // 2
        top = (resized.height - self.image_size) // 2
        base = resized.crop((left, top, left + self.image_size, top + self.image_size))
        heat_image = Image.fromarray((heatmap * 255).astype(np.uint8), mode="L")
        colored = ImageOps.colorize(heat_image, black="#10233f", mid="#f5b942", white="#d92d20")
        overlay = Image.blend(base, colored, alpha=0.42)
        buffer = BytesIO()
        overlay.save(buffer, format="PNG", optimize=True)
        return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
