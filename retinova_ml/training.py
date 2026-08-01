"""Reproducible training loop for the Retinova research baseline."""
import json
import random
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.metrics import confusion_matrix, f1_score, recall_score
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.transforms import InterpolationMode

from . import CLASS_NAMES
from .data import manifest_fingerprint
from .model import build_model


NORMALIZE = transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


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
                    image_size, scale=(0.82, 1.0), ratio=(0.95, 1.05), interpolation=mode
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


class FundusDataset(Dataset):
    def __init__(self, frame, transform):
        self.frame = frame.reset_index(drop=True)
        self.transform = transform

    def __len__(self):
        return len(self.frame)

    def __getitem__(self, index):
        row = self.frame.iloc[index]
        with Image.open(row["image_path"]) as source:
            image = source.convert("RGB")
        return self.transform(image), int(row["label_index"])


def make_loaders(manifest, batch_size, workers, image_size, seed=42, interpolation="bilinear"):
    loaders = {}
    for split in ("train", "val", "test"):
        subset = manifest.loc[manifest["split"] == split]
        dataset = FundusDataset(
            subset, build_transform(split == "train", image_size, interpolation=interpolation)
        )
        generator = torch.Generator().manual_seed(seed)
        loaders[split] = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=split == "train",
            num_workers=workers,
            pin_memory=torch.cuda.is_available(),
            persistent_workers=workers > 0 and split != "test",
            generator=generator,
        )
    return loaders


def compute_metrics(labels, predictions, class_names=CLASS_NAMES):
    labels = np.asarray(labels)
    predictions = np.asarray(predictions)
    matrix = confusion_matrix(labels, predictions, labels=range(len(class_names)))
    per_class_recall = recall_score(
        labels, predictions, labels=range(len(class_names)), average=None, zero_division=0
    )
    total = matrix.sum()
    specificity = {}
    for index, name in enumerate(class_names):
        true_positive = matrix[index, index]
        false_positive = matrix[:, index].sum() - true_positive
        false_negative = matrix[index, :].sum() - true_positive
        true_negative = total - true_positive - false_positive - false_negative
        denominator = true_negative + false_positive
        specificity[name] = float(true_negative / denominator) if denominator else 0.0
    return {
        "macro_f1": float(f1_score(labels, predictions, average="macro", zero_division=0)),
        "balanced_accuracy": float(per_class_recall.mean()),
        "per_class_recall": {
            name: float(value) for name, value in zip(class_names, per_class_recall, strict=True)
        },
        "per_class_specificity": specificity,
        "confusion_matrix": matrix.tolist(),
    }


def bootstrap_patient_metrics(
    labels, predictions, patient_ids, iterations=500, seed=42, class_names=CLASS_NAMES
):
    """Return patient-resampled 95% intervals for headline metrics."""
    labels = np.asarray(labels)
    predictions = np.asarray(predictions)
    patient_ids = np.asarray(patient_ids)
    if not (len(labels) == len(predictions) == len(patient_ids)):
        raise ValueError("labels, predictions, and patient_ids must have equal length")
    patients = np.unique(patient_ids)
    if not len(patients):
        raise ValueError("at least one patient is required")
    indices_by_patient = {patient: np.flatnonzero(patient_ids == patient) for patient in patients}
    generator = np.random.default_rng(seed)
    samples = {"macro_f1": [], "balanced_accuracy": []}
    for _ in range(iterations):
        sampled_patients = generator.choice(patients, size=len(patients), replace=True)
        sampled_indices = np.concatenate([indices_by_patient[patient] for patient in sampled_patients])
        metrics = compute_metrics(
            labels[sampled_indices], predictions[sampled_indices], class_names=class_names
        )
        for name in samples:
            samples[name].append(metrics[name])
    return {
        name: {
            "lower": float(np.percentile(values, 2.5)),
            "upper": float(np.percentile(values, 97.5)),
            "iterations": iterations,
            "unit": "patient",
        }
        for name, values in samples.items()
    }


def run_epoch(model, loader, criterion, device, optimizer=None, scaler=None, return_predictions=False):
    training = optimizer is not None
    model.train(training)
    total_loss = 0.0
    labels, predictions = [], []
    context = torch.enable_grad if training else torch.inference_mode
    with context():
        for images, targets in loader:
            images = images.to(device, non_blocking=True)
            targets = targets.to(device, non_blocking=True)
            if training:
                optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast(device_type=device.type, enabled=device.type == "cuda"):
                logits = model(images)
                loss = criterion(logits, targets)
            if training:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            total_loss += float(loss.detach()) * len(targets)
            labels.extend(targets.detach().cpu().tolist())
            predictions.extend(logits.argmax(dim=1).detach().cpu().tolist())
    metrics = compute_metrics(labels, predictions)
    metrics["loss"] = total_loss / len(loader.dataset)
    if return_predictions:
        return metrics, np.asarray(labels), np.asarray(predictions)
    return metrics


def git_revision():
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def train_from_config(config_path):
    config_path = Path(config_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    set_seed(config["seed"])
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = pd.read_csv(config["manifest"])
    loaders = make_loaders(
        manifest,
        config["batch_size"],
        config["workers"],
        config["image_size"],
        seed=config["seed"],
        interpolation=config.get("interpolation", "bilinear"),
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    architecture = config.get("architecture", "resnet18")
    model = build_model(architecture, len(CLASS_NAMES), pretrained=config["pretrained"]).to(device)
    counts = (
        manifest.loc[manifest["split"] == "train", "label_index"]
        .value_counts()
        .reindex(range(len(CLASS_NAMES)))
    )
    if counts.isna().any():
        raise ValueError("every class must occur in the training split")
    weights = counts.sum() / (len(CLASS_NAMES) * counts.to_numpy())
    criterion = nn.CrossEntropyLoss(weight=torch.tensor(weights, dtype=torch.float32, device=device))
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=config["learning_rate"], weight_decay=config["weight_decay"]
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config["epochs"])
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    checkpoint_path = output_dir / f"retinova_{architecture}_best.pt"
    history = []
    best_f1 = -1.0
    stale_epochs = 0
    for epoch in range(1, config["epochs"] + 1):
        train_metrics = run_epoch(model, loaders["train"], criterion, device, optimizer, scaler)
        val_metrics = run_epoch(model, loaders["val"], criterion, device)
        scheduler.step()
        record = {"epoch": epoch, "train": train_metrics, "val": val_metrics}
        history.append(record)
        print(
            f"epoch={epoch:02d} train_loss={train_metrics['loss']:.4f} "
            f"val_loss={val_metrics['loss']:.4f} val_macro_f1={val_metrics['macro_f1']:.4f}",
            flush=True,
        )
        if val_metrics["macro_f1"] > best_f1:
            best_f1 = val_metrics["macro_f1"]
            stale_epochs = 0
            torch.save(
                {
                    "state_dict": model.state_dict(),
                    "architecture": architecture,
                    "class_names": CLASS_NAMES,
                    "image_size": config["image_size"],
                    "normalization": {
                        "mean": [0.485, 0.456, 0.406],
                        "std": [0.229, 0.224, 0.225],
                    },
                    "preprocessing": {
                        "resize_short_side": 256,
                        "center_crop": config["image_size"],
                        "interpolation": config.get("interpolation", "bilinear"),
                    },
                    "best_validation_macro_f1": best_f1,
                    "config": config,
                    "manifest_fingerprint_sha256": manifest_fingerprint(manifest),
                    "git_revision": git_revision(),
                },
                checkpoint_path,
            )
        else:
            stale_epochs += 1
            if stale_epochs >= config["patience"]:
                print("early stopping", flush=True)
                break
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["state_dict"])
    test_metrics, test_labels, test_predictions = run_epoch(
        model, loaders["test"], criterion, device, return_predictions=True
    )
    test_patients = loaders["test"].dataset.frame["patient_id"].to_numpy()
    confidence_intervals = bootstrap_patient_metrics(
        test_labels, test_predictions, test_patients, seed=config["seed"]
    )
    report = {
        "status": "research baseline",
        "device": str(device),
        "checkpoint": str(checkpoint_path),
        "best_validation_macro_f1": best_f1,
        "test": test_metrics,
        "test_patient_bootstrap_95_ci": confidence_intervals,
        "history": history,
        "class_names": CLASS_NAMES,
        "manifest_fingerprint_sha256": manifest_fingerprint(manifest),
        "split_rows": manifest["split"].value_counts().to_dict(),
        "split_patients": manifest.groupby("split")["patient_id"].nunique().to_dict(),
    }
    report_path = output_dir / "evaluation_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"checkpoint": str(checkpoint_path), "test": test_metrics}, indent=2))
    return report
