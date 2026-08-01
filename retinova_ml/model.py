"""Versioned Retinova image-classification model factory."""
from torch import nn
from torchvision.models import (
    EfficientNet_B0_Weights,
    ResNet18_Weights,
    efficientnet_b0,
    resnet18,
)


SUPPORTED_ARCHITECTURES = ("resnet18", "efficientnet_b0")


def build_model(architecture, num_classes=8, pretrained=True):
    """Build a supported classifier with a task-specific output head."""
    if architecture == "resnet18":
        weights = ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        model = resnet18(weights=weights)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        return model
    if architecture == "efficientnet_b0":
        weights = EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
        model = efficientnet_b0(weights=weights)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        return model
    raise ValueError(
        f"unsupported architecture: {architecture!r}; expected one of {SUPPORTED_ARCHITECTURES}"
    )


def gradcam_target(model, architecture):
    """Return a convolutional feature layer and its stable provenance name."""
    if architecture == "resnet18":
        return model.layer4[-1].conv2, "layer4.1.conv2"
    if architecture == "efficientnet_b0":
        return model.features[-1], "features.8"
    raise ValueError(
        f"unsupported architecture: {architecture!r}; expected one of {SUPPORTED_ARCHITECTURES}"
    )


def build_resnet18(num_classes=8, pretrained=True):
    """Backward-compatible ResNet-18 constructor."""
    return build_model("resnet18", num_classes=num_classes, pretrained=pretrained)


def gradcam_target_layer(model):
    """Backward-compatible ResNet-18 Grad-CAM layer selector."""
    return gradcam_target(model, "resnet18")[0]
