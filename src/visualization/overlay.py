"""Draw annotated polygons on images for visual label inspection."""

from __future__ import annotations

import cv2
import numpy as np
from matplotlib import colors as mcolors

from src.datasets.yolo_seg import Instance


def color_bgr(name: str) -> tuple[int, int, int]:
    r, g, b = (int(round(c * 255)) for c in mcolors.to_rgb(name))
    return b, g, r


def resize_max_side(image: np.ndarray, max_side: int) -> np.ndarray:
    h, w = image.shape[:2]
    scale = max_side / max(h, w)
    if scale >= 1:
        return image
    return cv2.resize(image, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)


def draw_instances(
    image: np.ndarray,
    instances: list[Instance],
    class_names: dict[int, str],
    class_colors: dict[str, str],
    alpha: float = 0.35,
) -> np.ndarray:
    """Fill each polygon with its class color and outline it. `image` is BGR at display size."""
    h, w = image.shape[:2]
    fill = image.copy()
    out = image.copy()
    thickness = max(1, round(max(h, w) / 500))
    for inst in instances:
        pts = np.round(inst.polygon * [w, h]).astype(np.int32)
        color = color_bgr(class_colors[class_names[inst.class_id]])
        cv2.fillPoly(fill, [pts], color)
    out = cv2.addWeighted(fill, alpha, out, 1 - alpha, 0)
    for inst in instances:
        pts = np.round(inst.polygon * [w, h]).astype(np.int32)
        color = color_bgr(class_colors[class_names[inst.class_id]])
        cv2.polylines(out, [pts], True, color, thickness, cv2.LINE_AA)
    return out


def draw_legend(image: np.ndarray, counts: dict[str, int], class_colors: dict[str, str]) -> np.ndarray:
    out = image.copy()
    scale = max(image.shape[:2]) / 1600
    font, line_h = cv2.FONT_HERSHEY_SIMPLEX, round(36 * scale)
    box_w, box_h = round(330 * scale), line_h * len(counts) + round(16 * scale)
    cv2.rectangle(out, (0, 0), (box_w, box_h), (0, 0, 0), -1)
    for i, (name, n) in enumerate(counts.items()):
        y = round(10 * scale) + line_h * i
        cv2.rectangle(out, (round(10 * scale), y), (round(34 * scale), y + round(24 * scale)), color_bgr(class_colors[name]), -1)
        cv2.putText(out, f"{name}: {n}", (round(44 * scale), y + round(22 * scale)), font, 0.8 * scale,
                    (255, 255, 255), max(1, round(2 * scale)), cv2.LINE_AA)
    return out


def crop_instance(image: np.ndarray, inst: Instance, size: int, pad: float = 0.1) -> np.ndarray:
    """Square crop around the instance bbox with its outline, resized to `size`. `image` is full-res BGR."""
    h, w = image.shape[:2]
    pts = inst.polygon * [w, h]
    x0, y0 = pts.min(0)
    x1, y1 = pts.max(0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    half = max(x1 - x0, y1 - y0) * (0.5 + pad)
    left, top = int(max(0, cx - half)), int(max(0, cy - half))
    right, bottom = int(min(w, cx + half)), int(min(h, cy + half))
    crop = image[top:bottom, left:right].copy()
    local = np.round(pts - [left, top]).astype(np.int32)
    cv2.polylines(crop, [local], True, (255, 0, 255), max(1, round(max(crop.shape[:2]) / 150)), cv2.LINE_AA)
    ch, cw = crop.shape[:2]
    side = max(ch, cw)
    canvas = np.zeros((side, side, 3), np.uint8)
    canvas[(side - ch) // 2:(side - ch) // 2 + ch, (side - cw) // 2:(side - cw) // 2 + cw] = crop
    return cv2.resize(canvas, (size, size), interpolation=cv2.INTER_AREA)


def tile(images: list[np.ndarray], cols: int) -> np.ndarray:
    size = images[0].shape[0]
    rows = -(-len(images) // cols)
    grid = np.zeros((rows * size, cols * size, 3), np.uint8)
    for i, img in enumerate(images):
        r, c = divmod(i, cols)
        grid[r * size:(r + 1) * size, c * size:(c + 1) * size] = img
    return grid
