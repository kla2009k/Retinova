"""Re-evaluate a frozen Retinova checkpoint on its patient-grouped test set."""
import argparse
import json
from pathlib import Path

import pandas as pd
import torch
from torch import nn

from retinova_ml import CLASS_NAMES
from retinova_ml.data import manifest_fingerprint
from retinova_ml.model import build_model
from retinova_ml.training import bootstrap_patient_metrics, make_loaders, run_epoch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--manifest", default="artifacts/retinova_manifest.csv")
    parser.add_argument("--output", default="artifacts/evaluation_baseline_v1.json")
    parser.add_argument("--bootstrap-iterations", type=int, default=500)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    manifest = pd.read_csv(args.manifest)
    config = checkpoint["config"]
    loaders = make_loaders(
        manifest,
        batch_size=config["batch_size"],
        workers=config["workers"],
        image_size=checkpoint["image_size"],
        seed=config["seed"],
        interpolation=config.get("interpolation", "bilinear"),
    )
    model = build_model(
        checkpoint.get("architecture", "resnet18"), len(CLASS_NAMES), pretrained=False
    ).to(device)
    model.load_state_dict(checkpoint["state_dict"])
    train_counts = (
        manifest.loc[manifest["split"] == "train", "label_index"]
        .value_counts()
        .reindex(range(len(CLASS_NAMES)))
    )
    weights = train_counts.sum() / (len(CLASS_NAMES) * train_counts.to_numpy())
    criterion = nn.CrossEntropyLoss(weight=torch.tensor(weights, dtype=torch.float32, device=device))
    metrics, labels, predictions = run_epoch(
        model, loaders["test"], criterion, device, return_predictions=True
    )
    patients = loaders["test"].dataset.frame["patient_id"].to_numpy()
    report = {
        "status": "research baseline; not for clinical use",
        "architecture": checkpoint["architecture"],
        "class_names": checkpoint["class_names"],
        "image_size": checkpoint["image_size"],
        "model_revision": checkpoint.get("git_revision", "unknown"),
        "manifest_fingerprint_sha256": manifest_fingerprint(manifest),
        "split_policy": "StratifiedGroupKFold by patient; 70/15/15",
        "split_rows": manifest["split"].value_counts().to_dict(),
        "split_patients": manifest.groupby("split")["patient_id"].nunique().to_dict(),
        "patient_overlap": 0,
        "best_validation_macro_f1": checkpoint["best_validation_macro_f1"],
        "test": metrics,
        "test_patient_bootstrap_95_ci": bootstrap_patient_metrics(
            labels,
            predictions,
            patients,
            iterations=args.bootstrap_iterations,
            seed=config["seed"],
        ),
        "limitations": [
            "single-image labels are a reduction of the original bilateral ODIR task",
            "no external-site validation",
            "no clinical or regulatory approval",
            "ODIR redistribution and trained-weight licensing require clarification",
        ],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
