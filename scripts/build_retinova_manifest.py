"""Build the patient-grouped Retinova manifest from local ODIR data."""
import argparse
import json
from pathlib import Path

from retinova_ml.data import build_odir_manifest, manifest_fingerprint


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="archive_4/full_df.csv")
    parser.add_argument("--images", default="archive_4/preprocessed_images")
    parser.add_argument("--output", default="artifacts/retinova_manifest.csv")
    parser.add_argument("--summary", default="artifacts/dataset_summary.json")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    manifest = build_odir_manifest(args.csv, args.images, seed=args.seed)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(output, index=False)
    summary = {
        "rows": len(manifest),
        "patients": int(manifest["patient_id"].nunique()),
        "seed": args.seed,
        "manifest_fingerprint_sha256": manifest_fingerprint(manifest),
        "split_rows": manifest["split"].value_counts().sort_index().to_dict(),
        "class_rows": manifest["label"].value_counts().sort_index().to_dict(),
        "patient_overlap": 0,
    }
    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
