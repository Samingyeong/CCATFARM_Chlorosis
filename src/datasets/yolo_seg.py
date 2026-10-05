"""Reader for YOLO segmentation labels: one instance per line, `class_id x1 y1 x2 y2 ...` (0-1 normalized)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class Instance:
    class_id: int
    polygon: np.ndarray  # (N, 2) normalized x, y


def read_label_file(path: str | Path) -> list[Instance]:
    instances = []
    for line_no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        parts = line.split()
        if not parts:
            continue
        coords = parts[1:]
        if len(coords) < 6 or len(coords) % 2:
            raise ValueError(f"{path}:{line_no}: expected class id + >=3 (x, y) pairs, got {len(coords)} values")
        instances.append(Instance(int(parts[0]), np.asarray(coords, dtype=np.float64).reshape(-1, 2)))
    return instances


def list_samples(cfg: dict) -> list[tuple[Path, Path]]:
    """(image, label) pairs from `dataset.root`, matched by file stem."""
    ds = cfg["dataset"]
    root = Path(ds["root"])
    image_dir, label_dir = root / ds["images_dir"], root / ds["labels_dir"]
    if not image_dir.is_dir():
        raise FileNotFoundError(f"image dir not found: {image_dir}")
    pairs = []
    for image_path in sorted(p for p in image_dir.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"}):
        label_path = label_dir / f"{image_path.stem}.txt"
        if not label_path.exists():
            raise FileNotFoundError(f"missing label for {image_path.name}: {label_path}")
        pairs.append((image_path, label_path))
    return pairs
