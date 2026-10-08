"""Lightweight ONNX inference helpers for the Retinova web service."""

from __future__ import annotations

import base64
import json
from io import BytesIO
from pathlib import Path
from time import perf_counter

import numpy as np
from PIL import Image, ImageOps


IMAGENET_MEAN = np.asarray((0.485, 0.456, 0.406), dtype=np.float32)
IMAGENET_STD = np.asarray((0.229, 0.224, 0.225), dtype=np.float32)
INTERPOLATION_MODES = {
    "bilinear": Image.Resampling.BILINEAR,
    "bicubic": Image.Resampling.BICUBIC,
}
MAX_IMAGE_PIXELS = 24_000_000


def decode_candidate_image(image_bytes: bytes, image_size: int = 224) -> Image.Image:
    """Apply conservative technical checks before running the research model."""
    with Image.open(BytesIO(image_bytes)) as encoded:
        if encoded.format not in {"JPEG", "PNG"}:
            raise ValueError("only JPEG and PNG fundus images are accepted")
        if encoded.width * encoded.height > MAX_IMAGE_PIXELS:
            raise ValueError("image dimensions exceed the 24 megapixel limit")
        source = encoded.convert("RGB")
    if min(source.size) < image_size:
        raise ValueError(f"image must be at least {image_size} px on its shortest side")
    ratio = source.width / source.height
    if ratio < 0.5 or ratio > 2.0:
        raise ValueError("image aspect ratio is outside the accepted range")
    # This catches only near-uniform uploads; it does not establish fundus quality.
    thumbnail = np.asarray(source.resize((64, 64)).convert("L"), dtype=np.uint8)
    if int(thumbnail.max()) - int(thumbnail.min()) < 8:
        raise ValueError("image appears blank or has insufficient visual contrast")
    return source


def _resample_mode(name: str) -> Image.Resampling:
    try:
        return INTERPOLATION_MODES[name]
    except KeyError as error:
        raise ValueError(
            f"unsupported interpolation: {name!r}; expected one of {tuple(INTERPOLATION_MODES)}"
        ) from error


def _resize_and_center_crop(
    image: Image.Image, image_size: int, interpolation: str
) -> Image.Image:
    """Match torchvision Resize(256) + CenterCrop(image_size)."""
    resample = _resample_mode(interpolation)
    resize_size = 256
    width, height = image.size
    if width <= height:
        resized_width = resize_size
        resized_height = int(resize_size * height / width)
    else:
        resized_height = resize_size
        resized_width = int(resize_size * width / height)

    resized = image.resize((resized_width, resized_height), resample=resample)
    left = (resized_width - image_size) // 2
    top = (resized_height - image_size) // 2
    return resized.crop((left, top, left + image_size, top + image_size))


def preprocess_image(
    image: Image.Image, image_size: int = 224, interpolation: str = "bilinear"
) -> np.ndarray:
    cropped = _resize_and_center_crop(image.convert("RGB"), image_size, interpolation)
    pixels = np.asarray(cropped, dtype=np.float32) / np.float32(255.0)
    normalized = (pixels - IMAGENET_MEAN) / IMAGENET_STD
    return np.transpose(normalized, (2, 0, 1))[None].astype(np.float32, copy=False)


def normalize_cam(cam: np.ndarray, image_size: int) -> np.ndarray:
    values = np.asarray(cam, dtype=np.float32)
    if values.ndim != 2:
        raise ValueError(f"CAM must be a 2D array, received shape {values.shape}")
    values = np.maximum(values, np.float32(0.0))
    image = Image.fromarray(values, mode="F").resize(
        (image_size, image_size), resample=Image.Resampling.BILINEAR
    )
    resized = np.asarray(image, dtype=np.float32)
    minimum = float(resized.min())
    maximum = float(resized.max())
    if not np.isfinite(resized).all() or maximum - minimum <= np.finfo(np.float32).eps:
        return np.zeros((image_size, image_size), dtype=np.float32)
    return ((resized - minimum) / (maximum - minimum)).astype(np.float32, copy=False)


def _softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - np.max(logits)
    exponentials = np.exp(shifted)
    return exponentials / exponentials.sum()


class RetinovaONNXPredictor:
    """Run Retinova classification and class activation mapping on CPU."""

    def __init__(self, model_path: str | Path, metadata_path: str | Path):
        import onnxruntime as ort

        with Path(metadata_path).open("r", encoding="utf-8") as handle:
            metadata = json.load(handle)
        self.class_names = list(metadata["class_names"])
        self.image_size = int(metadata["image_size"])
        self.architecture = metadata["architecture"]
        self.interpolation = metadata.get("interpolation", "bilinear")
        self.model_revision = metadata.get("model_revision", "unknown")
        self.target_layer = metadata.get("target_layer", "features")

        options = ort.SessionOptions()
        options.intra_op_num_threads = 1
        options.inter_op_num_threads = 1
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(
            str(model_path), sess_options=options, providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, image_bytes: bytes) -> dict:
        started_at = perf_counter()
        source = decode_candidate_image(image_bytes, self.image_size)

        tensor = preprocess_image(source, self.image_size, self.interpolation)
        logits_batch, cams_batch = self.session.run(None, {self.input_name: tensor})
        probabilities = _softmax(np.asarray(logits_batch[0], dtype=np.float32))
        predicted_index = int(probabilities.argmax())
        heatmap = normalize_cam(cams_batch[0, predicted_index], self.image_size)
        overlay = self._overlay(source, heatmap)
        return {
            "prediction": self.class_names[predicted_index],
            "probability": float(probabilities[predicted_index]),
            "probabilities": {
                name: float(value)
                for name, value in zip(self.class_names, probabilities, strict=True)
            },
            "gradcam_data_url": overlay,
            "inference_ms": round((perf_counter() - started_at) * 1000),
            "provenance": {
                "architecture": self.architecture,
                "model_revision": self.model_revision,
                "target_class": self.class_names[predicted_index],
                "target_layer": self.target_layer,
                "attribution_method": "class_activation_mapping",
                "interpretation": "model attribution, not lesion segmentation",
            },
            "warning": "research screening output; not a medical diagnosis",
        }

    def _overlay(self, source: Image.Image, heatmap: np.ndarray) -> str:
        base = _resize_and_center_crop(source.convert("RGB"), self.image_size, self.interpolation)
        heat_image = Image.fromarray((heatmap * 255).astype(np.uint8), mode="L")
        colored = ImageOps.colorize(
            heat_image, black="#10233f", mid="#f5b942", white="#d92d20"
        )
        overlay = Image.blend(base, colored, alpha=0.42)
        buffer = BytesIO()
        overlay.save(buffer, format="PNG", optimize=True)
        return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
