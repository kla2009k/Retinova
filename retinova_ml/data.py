"""Dataset validation and patient-grouped split utilities."""
import ast
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from . import CLASS_NAMES


def manifest_fingerprint(frame):
    """Hash identity, label, and split fields without machine-specific paths."""
    columns = ["patient_id", "filename", "label", "label_index", "split"]
    if missing := set(columns).difference(frame.columns):
        raise ValueError(f"cannot fingerprint manifest; missing columns: {sorted(missing)}")
    canonical = frame[columns].to_csv(index=False, lineterminator="\n").encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def assign_grouped_splits(frame, group_col, label_col, seed=42, n_folds=20):
    """Return a copy with deterministic 70/15/15 patient-disjoint splits.

    StratifiedGroupKFold attempts to retain class proportions while ensuring a
    group occurs in only one fold. Twenty folds map exactly to 14/3/3 folds.
    """
    if n_folds != 20:
        raise ValueError("n_folds must be 20 for the 70/15/15 policy")
    required = {group_col, label_col}
    if missing := required.difference(frame.columns):
        raise ValueError(f"missing columns: {sorted(missing)}")
    if frame[group_col].nunique() < n_folds:
        raise ValueError("at least 20 patient groups are required")
    result = frame.copy().reset_index(drop=True)
    result["split"] = ""
    splitter = StratifiedGroupKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    placeholder = np.zeros(len(result), dtype=np.uint8)
    for fold, (_, held_out) in enumerate(
        splitter.split(placeholder, result[label_col], groups=result[group_col])
    ):
        split = "train" if fold < 14 else "val" if fold < 17 else "test"
        result.loc[held_out, "split"] = split
    if (result["split"] == "").any():
        raise RuntimeError("split assignment was incomplete")
    leakage = result.groupby(group_col)["split"].nunique().max()
    if leakage != 1:
        raise RuntimeError("patient leakage detected")
    return result


def build_odir_manifest(csv_path, image_dir, seed=42):
    """Validate the local ODIR-derived table and return a training manifest."""
    csv_path = Path(csv_path).resolve()
    image_dir = Path(image_dir).resolve()
    frame = pd.read_csv(csv_path)
    required = {"ID", "filename", "target"}
    if missing := required.difference(frame.columns):
        raise ValueError(f"missing ODIR columns: {sorted(missing)}")
    try:
        targets = np.asarray([ast.literal_eval(str(value)) for value in frame["target"]], dtype=int)
    except (SyntaxError, ValueError, TypeError) as error:
        raise ValueError("target contains an invalid serialized label vector") from error
    if targets.shape != (len(frame), len(CLASS_NAMES)):
        raise ValueError(f"target must contain {len(CLASS_NAMES)} values per image")
    invalid = (targets.sum(axis=1) != 1) | ~np.isin(targets, (0, 1)).all(axis=1)
    if invalid.any():
        raise ValueError(f"{int(invalid.sum())} target rows are not single-label one-hot records")
    label_indices = targets.argmax(axis=1)
    manifest = pd.DataFrame(
        {
            "patient_id": frame["ID"].astype(str),
            "filename": frame["filename"].astype(str),
            "label": [CLASS_NAMES[index] for index in label_indices],
            "label_index": label_indices,
        }
    )
    manifest["image_path"] = manifest["filename"].map(lambda name: str(image_dir / name))
    exists = manifest["image_path"].map(lambda path: Path(path).is_file())
    if not exists.all():
        sample = manifest.loc[~exists, "image_path"].head(3).tolist()
        raise FileNotFoundError(f"{int((~exists).sum())} images are missing; examples: {sample}")
    return assign_grouped_splits(manifest, "patient_id", "label_index", seed=seed)
