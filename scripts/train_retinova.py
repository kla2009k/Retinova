"""Train and evaluate the Retinova patient-grouped baseline."""
import argparse

from retinova_ml.training import train_from_config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/train_resnet18.json")
    args = parser.parse_args()
    train_from_config(args.config)


if __name__ == "__main__":
    main()
