"""Record the execution environment (Python, PyTorch, CUDA, GPU, package versions).

Usage:
    python scripts/check_env.py [--out-dir outputs/env]

Writes a timestamped JSON report so each machine (local PC, lab server) is documented.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PACKAGES = [
    "torch",
    "torchvision",
    "transformers",
    "accelerate",
    "timm",
    "numpy",
    "pandas",
    "pillow",
    "opencv-python",
    "pycocotools",
    "scikit-learn",
    "matplotlib",
    "pyyaml",
    "tqdm",
]


def package_versions() -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for name in PACKAGES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def torch_info() -> dict:
    try:
        import torch
    except ImportError as exc:
        return {"installed": False, "error": str(exc)}

    info = {
        "installed": True,
        "version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda,
        "cudnn_version": torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else None,
        "devices": [],
    }
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            info["devices"].append(
                {
                    "index": i,
                    "name": props.name,
                    "total_memory_gb": round(props.total_memory / 1024**3, 2),
                    "capability": f"{props.major}.{props.minor}",
                }
            )
    return info


def nvidia_smi() -> str | None:
    """Raw nvidia-smi output (driver version etc.); None when no NVIDIA driver is present."""
    if shutil.which("nvidia-smi") is None:
        return None
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else f"error: {result.stderr.strip()}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path("outputs/env"))
    args = parser.parse_args()

    report = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "hostname": platform.node(),
        "os": platform.platform(),
        "python": sys.version,
        "python_executable": sys.executable,
        "torch": torch_info(),
        "nvidia_smi": nvidia_smi(),
        "packages": package_versions(),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_path = args.out_dir / f"env_{platform.node()}_{stamp}.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
