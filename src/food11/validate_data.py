"""Validate the processed Food-11 data contract before training."""
import argparse
import hashlib
from pathlib import Path

from PIL import Image

try:
    from .data import CLASSES, SPLITS
except ImportError:
    from data import CLASSES, SPLITS


def validate(root, min_per_class=50, tau=0.05):
    checks = dict.fromkeys(["class folders", "image format", "minimum counts", "split leakage", "class balance"], True)
    counts = {}
    seen = {}
    for split in SPLITS:
        folder = root / split
        folders = {p.name for p in folder.iterdir() if p.is_dir()} if folder.is_dir() else set()
        checks["class folders"] &= folders == set(CLASSES)
        counts[split] = {}
        for category in CLASSES:
            class_dir = folder / category
            files = sorted(p for p in class_dir.rglob("*") if p.is_file()) if class_dir.is_dir() else []
            counts[split][category] = len(files)
            checks["minimum counts"] &= len(files) >= min_per_class
            for path in files:
                try:
                    with Image.open(path) as image:
                        image.load()
                        checks["image format"] &= image.mode == "RGB" and image.size == (128, 128)
                    digest = hashlib.md5(path.read_bytes()).hexdigest()
                    if digest in seen and seen[digest] != split:
                        checks["split leakage"] = False
                    seen.setdefault(digest, split)
                except (OSError, ValueError):
                    checks["image format"] = False
    train_total = sum(counts["training"].values())
    val_total = sum(counts["validation"].values())
    if not train_total or not val_total:
        checks["class balance"] = False
    else:
        for category in CLASSES:
            difference = abs(counts["training"][category] / train_total - counts["validation"][category] / val_total)
            checks["class balance"] &= difference <= tau
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {name}")
    return all(checks.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--min-per-class", type=int, default=50)
    parser.add_argument("--tau", type=float, default=0.05)
    args = parser.parse_args()
    if args.min_per_class < 1 or not 0 <= args.tau <= 1:
        parser.error("min-per-class must be positive and tau must be between 0 and 1")
    raise SystemExit(0 if validate(args.dataset, args.min_per_class, args.tau) else 1)


if __name__ == "__main__":
    main()
