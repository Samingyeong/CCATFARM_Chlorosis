"""Visual inspection of the raw YOLO-seg labels (Phase 1). Reads data only; never modifies it.

Usage (from repo root):
    python scripts/visualize_labels.py [--config configs/base.yaml] [--out-dir outputs/inspection/labels]

Writes:
    overlays/<stem>.jpg      polygons filled by class color + legend
    crops/<class>.jpg        random instance crops per class (polygon outlined in magenta)
    summary.json             per-class polygon size / vertex stats and selected images
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.datasets.yolo_seg import read_label_file, list_samples  # noqa: E402
from src.utils.config import load_config  # noqa: E402
from src.visualization.overlay import crop_instance, draw_instances, draw_legend, resize_max_side, tile  # noqa: E402


def polygon_area(poly: np.ndarray) -> float:
    x, y = poly[:, 0], poly[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def percentiles(values: list[float]) -> dict[str, float]:
    p = np.percentile(values, [0, 5, 50, 95, 100])
    return dict(zip(["min", "p5", "median", "p95", "max"], (round(float(v), 6) for v in p)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--out-dir", default=None, help="default: <paths.output_root>/inspection/labels")
    parser.add_argument("--per-class", type=int, default=2, help="overlay images with most instances of each class")
    parser.add_argument("--random-images", type=int, default=3, help="extra random overlay images")
    parser.add_argument("--crops-per-class", type=int, default=30)
    parser.add_argument("--crop-size", type=int, default=224)
    parser.add_argument("--images", nargs="*", default=[], help="extra image stems to overlay, e.g. IMG_070")
    parser.add_argument("--max-side", type=int, default=1600, help="overlay output size")
    args = parser.parse_args()

    cfg = load_config(args.config)
    class_names = {int(k): v for k, v in cfg["raw_class_map"].items()}
    class_colors = cfg["visualization"]["colors"]
    rng = random.Random(cfg["seed"])
    out_dir = Path(args.out_dir or Path(cfg["paths"]["output_root"]) / "inspection" / "labels")
    (out_dir / "overlays").mkdir(parents=True, exist_ok=True)
    (out_dir / "crops").mkdir(parents=True, exist_ok=True)

    samples = list_samples(cfg)
    labels = {img: read_label_file(lbl) for img, lbl in samples}
    unknown_ids = {i for inst in labels.values() for i in {x.class_id for x in inst}} - class_names.keys()
    if unknown_ids:
        raise ValueError(f"class ids not in raw_class_map: {sorted(unknown_ids)}")

    # Per-class geometry stats (area as fraction of image, vertex count)
    areas, vertices = defaultdict(list), defaultdict(list)
    for insts in labels.values():
        for inst in insts:
            name = class_names[inst.class_id]
            areas[name].append(polygon_area(inst.polygon))
            vertices[name].append(len(inst.polygon))

    # Overlay selection: images richest in each class + a few random ones
    selected: dict[Path, str] = {}
    for cid, name in class_names.items():
        ranked = sorted(labels, key=lambda p: -sum(i.class_id == cid for i in labels[p]))
        for p in ranked[: args.per_class]:
            selected.setdefault(p, f"most {name}")
    rest = [p for p in labels if p not in selected]
    for p in rng.sample(rest, min(args.random_images, len(rest))):
        selected[p] = "random"
    by_stem = {p.stem: p for p in labels}
    for stem in args.images:
        if stem not in by_stem:
            raise ValueError(f"image not found: {stem}")
        selected.setdefault(by_stem[stem], "requested")

    for img_path, reason in selected.items():
        image = cv2.imread(str(img_path))
        insts = labels[img_path]
        counts = {n: sum(class_names[i.class_id] == n for i in insts) for n in class_names.values()}
        vis = draw_instances(resize_max_side(image, args.max_side), insts, class_names, class_colors)
        vis = draw_legend(vis, counts, class_colors)
        cv2.imwrite(str(out_dir / "overlays" / f"{img_path.stem}.jpg"), vis, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"overlay {img_path.name} ({reason})")

    # Crop galleries: sample instances per class, load each image once
    by_image = defaultdict(list)
    crop_sources = {}
    for cid, name in class_names.items():
        pool = [(p, k) for p, insts in labels.items() for k, i in enumerate(insts) if i.class_id == cid]
        picked = rng.sample(pool, min(args.crops_per_class, len(pool)))
        crop_sources[name] = [f"{p.stem}#{k}" for p, k in picked]
        for p, k in picked:
            by_image[p].append((name, k))
    crops = defaultdict(list)
    for img_path, items in by_image.items():
        image = cv2.imread(str(img_path))
        for name, k in items:
            crops[name].append(crop_instance(image, labels[img_path][k], args.crop_size))
    for name, imgs in crops.items():
        fname = name.lower().replace(" ", "_")
        cv2.imwrite(str(out_dir / "crops" / f"{fname}.jpg"), tile(imgs, cols=6), [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"crops {name}: {len(imgs)}")

    summary = {
        "config": args.config,
        "num_images": len(samples),
        "overlays": {p.stem: r for p, r in selected.items()},
        "crop_sources": crop_sources,
        "per_class": {
            name: {
                "instances": len(areas[name]),
                "area_fraction": percentiles(areas[name]),
                "vertices": percentiles(vertices[name]),
            }
            for name in class_names.values()
        },
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
