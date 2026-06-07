#!/usr/bin/env python3
"""Crop porcelain tile images to square and resize to 800x800 for crisp display (like marble)."""
import subprocess
import sys
from pathlib import Path

IMG_DIR = Path(__file__).parent.parent / "images" / "porcelain"
TARGET = 800


def get_size(path):
    out = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    w = h = None
    for line in out.stdout.strip().split("\n"):
        if "pixelWidth" in line:
            w = int(line.split(":")[-1].strip())
        elif "pixelHeight" in line:
            h = int(line.split(":")[-1].strip())
    return w, h


def main():
    if not IMG_DIR.exists():
        print("No images/porcelain directory.")
        return
    for p in sorted(IMG_DIR.glob("*.png")) + sorted(IMG_DIR.glob("*.jpg")):
        if p.name.startswith("_"):
            continue
        w, h = get_size(p)
        if w is None or h is None:
            continue
        dim = min(w, h)
        if dim < 2:
            continue
        # Center crop to square
        subprocess.run(["sips", "-c", str(dim), str(dim), str(p)], check=True, capture_output=True)
        # Resize to target for crisp display (downscale or modest upscale)
        subprocess.run(["sips", "-z", str(TARGET), str(TARGET), str(p)], check=True, capture_output=True)
        print(f"  {p.name}: {w}x{h} -> {TARGET}x{TARGET} (square)")


if __name__ == "__main__":
    main()
