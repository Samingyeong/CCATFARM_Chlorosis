"""YAML config loading with `base:` inheritance."""

from __future__ import annotations

from pathlib import Path

import yaml


def _merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path) -> dict:
    """Load a config file. A `base:` key (relative to the file) is loaded first and overridden."""
    path = Path(path)
    with path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    base = cfg.pop("base", None)
    if base:
        cfg = _merge(load_config(path.parent / base), cfg)
    return cfg
