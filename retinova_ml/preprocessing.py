"""Shared image preprocessing without training-only dependencies."""
from torchvision import transforms
from torchvision.transforms import InterpolationMode


NORMALIZE = transforms.Normalize(
    mean=(0.485, 0.456, 0.406),
    std=(0.229, 0.224, 0.225),
)


def _interpolation_mode(name):
    modes = {"bilinear": InterpolationMode.BILINEAR, "bicubic": InterpolationMode.BICUBIC}
    try:
        return modes[name]
    except KeyError as error:
        raise ValueError(
            f"unsupported interpolation: {name!r}; expected one of {tuple(modes)}"
        ) from error


def build_transform(training, image_size=224, interpolation="bilinear"):
    mode = _interpolation_mode(interpolation)
    if training:
        return transforms.Compose(
            [
                transforms.RandomResizedCrop(
                    image_size,
                    scale=(0.82, 1.0),
                    ratio=(0.95, 1.05),
                    interpolation=mode,
                ),
                transforms.RandomHorizontalFlip(),
                transforms.RandomRotation(8),
                transforms.ColorJitter(brightness=0.12, contrast=0.12, saturation=0.08),
                transforms.ToTensor(),
                NORMALIZE,
            ]
        )
    return transforms.Compose(
        [
            transforms.Resize(256, interpolation=mode),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            NORMALIZE,
        ]
    )
