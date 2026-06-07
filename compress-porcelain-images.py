#!/usr/bin/env python3
"""Compress large porcelain PNGs to JPEG and update HTML references."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORCELAIN_DIR = ROOT / "images" / "porcelain"
MIN_SIZE = 1 * 1024 * 1024  # 1 MB
MAX_DIMENSION = 1600
JPEG_QUALITY = 85


def compress_png(png_path: Path) -> Path | None:
    jpg_path = png_path.with_suffix(".jpg")
    subprocess.run(
        [
            "sips",
            "-Z",
            str(MAX_DIMENSION),
            str(png_path),
            "--out",
            str(jpg_path),
            "-s",
            "format",
            "jpeg",
            "-s",
            "formatOptions",
            str(JPEG_QUALITY),
        ],
        check=True,
        capture_output=True,
    )
    if not jpg_path.exists():
        return None
    png_path.unlink()
    return jpg_path


def update_html(converted: dict[str, str]) -> int:
    updated_files = 0
    for html_path in ROOT.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        new_text = text
        for stem in converted:
            new_text = new_text.replace(
                f"images/porcelain/{stem}.png",
                f"images/porcelain/{stem}.jpg",
            )
            new_text = new_text.replace(
                f"../images/porcelain/{stem}.png",
                f"../images/porcelain/{stem}.jpg",
            )
        if new_text != text:
            html_path.write_text(new_text, encoding="utf-8")
            updated_files += 1
    return updated_files


def main() -> None:
    converted: dict[str, str] = {}
    total_saved = 0

    for png_path in sorted(PORCELAIN_DIR.glob("*.png")):
        size = png_path.stat().st_size
        if size <= MIN_SIZE:
            continue
        jpg_path = compress_png(png_path)
        if jpg_path is None:
            continue
        new_size = jpg_path.stat().st_size
        total_saved += size - new_size
        converted[png_path.stem] = jpg_path.name
        print(f"{png_path.name}: {size // 1024 // 1024}MB -> {new_size // 1024}KB")

    if not converted:
        print("No large PNGs found.")
        return

    html_count = update_html(converted)
    print(f"\nConverted {len(converted)} images")
    print(f"Saved ~{total_saved // 1024 // 1024}MB total")
    print(f"Updated {html_count} HTML files")


if __name__ == "__main__":
    main()
