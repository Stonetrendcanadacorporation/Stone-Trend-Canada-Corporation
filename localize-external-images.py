#!/usr/bin/env python3
"""Download external image URLs and replace references with local assets."""
from __future__ import annotations

import hashlib
import json
import re
import ssl
import subprocess
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

try:
    from PIL import Image
    import io
except ImportError:
    Image = None
    io = None

ROOT = Path(__file__).parent.parent
SIZE = 400

MATERIAL_CONFIG = [
    ("data/olympia-marble.json", "images/marble"),
    ("data/olympia-travertine.json", "images/travertine"),
    ("data/olympia-granite.json", "images/granite"),
    ("data/olympia-porcelain.json", "images/porcelain/thumbs"),
]

MISC_DOWNLOADS = [
    (
        "https://images.pexels.com/photos/2079236/pexels-photo-2079236.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "images/gallery/backgrounds/res-1.jpg",
    ),
    (
        "https://images.pexels.com/photos/3753436/pexels-photo-3753436.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "images/gallery/backgrounds/res-2.jpg",
    ),
    (
        "https://images.pexels.com/photos/279719/pexels-photo-279719.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "images/gallery/backgrounds/res-3.jpg",
    ),
    (
        "https://images.pexels.com/photos/2802097/pexels-photo-2802097.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "images/gallery/backgrounds/com-1.jpg",
    ),
    (
        "https://images.pexels.com/photos/3735410/pexels-photo-3735410.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "images/gallery/backgrounds/com-2.jpg",
    ),
    (
        "https://images.pexels.com/photos/3735417/pexels-photo-3735417.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "images/gallery/backgrounds/com-3.jpg",
    ),
    (
        "https://mattamy-crhratfjdcd2g9gq.z01.azurefd.net/-/media/feature/content/identity/mattamylogo.svg",
        "images/logos/mattamy.svg",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/e/e7/Marriott_International.svg",
        "images/logos/marriott.svg",
    ),
]

PEXELS_REPLACEMENTS = {
    "https://images.pexels.com/photos/2079236/pexels-photo-2079236.jpeg?auto=compress&cs=tinysrgb&w=1200": "../images/gallery/backgrounds/res-1.jpg",
    "https://images.pexels.com/photos/3753436/pexels-photo-3753436.jpeg?auto=compress&cs=tinysrgb&w=1200": "../images/gallery/backgrounds/res-2.jpg",
    "https://images.pexels.com/photos/279719/pexels-photo-279719.jpeg?auto=compress&cs=tinysrgb&w=1200": "../images/gallery/backgrounds/res-3.jpg",
    "https://images.pexels.com/photos/2802097/pexels-photo-2802097.jpeg?auto=compress&cs=tinysrgb&w=1200": "../images/gallery/backgrounds/com-1.jpg",
    "https://images.pexels.com/photos/3735410/pexels-photo-3735410.jpeg?auto=compress&cs=tinysrgb&w=1200": "../images/gallery/backgrounds/com-2.jpg",
    "https://images.pexels.com/photos/3735417/pexels-photo-3735417.jpeg?auto=compress&cs=tinysrgb&w=1200": "../images/gallery/backgrounds/com-3.jpg",
}


def download_url(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
    )
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=60, context=ctx) as response:
        data = response.read()
    if data[:15].lower().startswith(b"<!doctype") or data[:6].lower().startswith(b"<html"):
        raise ValueError("response is HTML, not an image")
    return data


def ext_from_url(url: str, data: bytes) -> str:
    path = urlparse(url).path.lower()
    for ext in (".jpeg", ".jpg", ".png", ".webp", ".gif", ".svg"):
        if path.endswith(ext):
            return ".jpg" if ext == ".jpeg" else ext
    if data[:4] == b"\x89PNG":
        return ".png"
    if data[:2] == b"\xff\xd8":
        return ".jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    if b"<svg" in data[:500].lower():
        return ".svg"
    return ".jpg"


def to_square(data: bytes, size: int = SIZE):
    if not Image or not io:
        return None
    img = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    cropped = img.crop((left, top, left + side, top + side))
    return cropped.resize((size, size), Image.Resampling.LANCZOS)


def save_image(url: str, out_path: Path, square_thumb: bool = True) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    raw = download_url(url)
    ext = ext_from_url(url, raw)
    if out_path.suffix.lower() != ext and ext != ".svg":
        out_path = out_path.with_suffix(ext)

    if ext == ".svg":
        out_path.write_bytes(raw)
        return

    if square_thumb and ext in (".jpg", ".jpeg", ".png", ".webp"):
        squared = to_square(raw)
        if squared is not None:
            final = out_path.with_suffix(".jpg")
            squared.save(final, "JPEG", quality=88)
            return
    out_path.write_bytes(raw)


def download_material_images() -> dict[str, str]:
    """Download slab images from JSON catalogs. Returns url -> local path map."""
    mapping: dict[str, str] = {}
    stats = []

    for rel_data, rel_dir in MATERIAL_CONFIG:
        data_path = ROOT / rel_data
        if not data_path.exists():
            continue
        slabs = json.loads(data_path.read_text())
        img_dir = ROOT / rel_dir
        img_dir.mkdir(parents=True, exist_ok=True)
        ok = skip = err = 0

        for slab in slabs:
            slug = (slab.get("slug") or "").strip()
            if not slug:
                continue
            url = slab.get("img_large") or slab.get("img_small") or ""
            if not url.startswith("http"):
                if url.startswith("images/"):
                    skip += 1
                continue

            out_path = img_dir / f"{slug}.jpg"
            rel_local = str(out_path.relative_to(ROOT)).replace("\\", "/")
            if out_path.exists() and out_path.stat().st_size > 500:
                slab["img_small"] = rel_local
                slab["img_large"] = rel_local
                mapping[url] = rel_local
                skip += 1
                continue

            try:
                save_image(url, out_path, square_thumb=True)
                rel_local = str(out_path.relative_to(ROOT)).replace("\\", "/")
                slab["img_small"] = rel_local
                slab["img_large"] = rel_local
                mapping[url] = rel_local
                ok += 1
            except Exception as exc:
                print(f"  Skip {slug}: {exc}")
                err += 1

        data_path.write_text(json.dumps(slabs, indent=2) + "\n")
        stats.append((rel_data, ok, skip, err))

    for rel_data, ok, skip, err in stats:
        print(f"{rel_data}: downloaded={ok} already_local={skip} errors={err}")
    return mapping


def download_misc_images() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for url, rel_path in MISC_DOWNLOADS:
        out_path = ROOT / rel_path
        try:
            if not out_path.exists() or out_path.stat().st_size < 100:
                save_image(url, out_path, square_thumb=False)
            mapping[url] = rel_path
            print(f"Saved misc: {rel_path}")
        except Exception as exc:
            print(f"  Misc skip {rel_path}: {exc}")
    return mapping


def relative_local_path(file_path: Path, local_path: str) -> str:
    local = Path(local_path)
    rel = Path(os_path_relpath(local, file_path.parent))
    return str(rel).replace("\\", "/")


def os_path_relpath(target: Path, start: Path) -> str:
    target_parts = target.parts
    start_parts = start.parts
    common = 0
    for a, b in zip(start_parts, target_parts):
        if a != b:
            break
        common += 1
    ups = [".."] * (len(start_parts) - common)
    return "/".join(ups + list(target_parts[common:]))


def replace_urls_in_files(mapping: dict[str, str]) -> int:
    patterns = [
        (re.compile(r'src=(["\'])(https?://[^"\']+)\1'), "src"),
        (re.compile(r'url\((["\']?)(https?://[^"\')]+)\1\)'), "css"),
    ]
    changed_files = 0

    for path in list(ROOT.rglob("*.html")) + [ROOT / "css" / "styles.css"]:
        if not path.exists():
            continue
        text = path.read_text()
        original = text

        for regex, _kind in patterns:
            def repl(match, regex=regex):
                quote = match.group(1) if regex.pattern.startswith("src") else match.group(1)
                url = match.group(2) if regex.pattern.startswith("src") else match.group(2)
                if "google.com/maps" in url:
                    return match.group(0)
                local = mapping.get(url)
                if not local:
                    return match.group(0)
                if regex.pattern.startswith("url"):
                    if path.name == "styles.css" and url in PEXELS_REPLACEMENTS:
                        local_ref = PEXELS_REPLACEMENTS[url]
                    else:
                        local_ref = relative_local_path(path, local)
                    q = quote or '"'
                    return f"url({q}{local_ref}{q})"
                local_ref = relative_local_path(path, local)
                return f'src="{local_ref}"'

            text = regex.sub(repl, text)

        if text != original:
            path.write_text(text)
            changed_files += 1
    return changed_files


def regenerate_pages() -> None:
    scripts = [
        "build-marble-page.py",
        "generate-marble-detail-pages.py",
        "build-travertine-page.py",
        "generate-travertine-detail-pages.py",
        "build-granite-page.py",
        "generate-granite-detail-pages.py",
        "build-porcelain-page.py",
        "generate-porcelain-detail-pages.py",
    ]
    scripts_dir = ROOT / "scripts"
    for name in scripts:
        script = scripts_dir / name
        if script.exists():
            print(f"Running {name}...")
            subprocess.run([sys.executable, str(script)], check=True, cwd=ROOT)


def verify_images() -> tuple[int, int]:
    bad_files = 0
    external = 0
    img_ext = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}

    for path in ROOT.rglob("*"):
        if path.suffix.lower() in img_ext and "images" in path.parts:
            try:
                data = path.read_bytes()[:200]
                if data[:15].lower().startswith(b"<!doctype") or data[:6].lower().startswith(b"<html"):
                    bad_files += 1
            except OSError:
                bad_files += 1

    for path in list(ROOT.rglob("*.html")) + [ROOT / "css" / "styles.css"]:
        if not path.exists():
            continue
        text = path.read_text()
        for url in re.findall(r'(?:src=|url\()["\']?(https?://[^"\')\s]+)', text):
            if "google.com/maps" in url:
                continue
            if any(x in url.lower() for x in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", "pexels", "olympiatile", "wikimedia", "azurefd"]):
                external += 1
    return bad_files, external


def main() -> None:
    print("Downloading material catalog images...")
    mapping = download_material_images()
    print("Downloading misc images...")
    mapping.update(download_misc_images())

    # Hash-based fallback for any remaining unique external image URLs.
    print("Scanning for remaining external image URLs...")
    url_pattern = re.compile(r'(?:src=|url\()["\']?(https?://[^"\')\s]+)')
    remaining: set[str] = set()
    for path in list(ROOT.rglob("*.html")) + [ROOT / "css" / "styles.css"]:
        if not path.exists():
            continue
        for url in url_pattern.findall(path.read_text()):
            if "google.com/maps" in url:
                continue
            if url not in mapping:
                remaining.add(url)

    ext_dir = ROOT / "images" / "external"
    for url in sorted(remaining):
        digest = hashlib.sha1(url.encode()).hexdigest()[:12]
        parsed = urlparse(url)
        ext = Path(parsed.path).suffix.lower() or ".jpg"
        if ext == ".jpeg":
            ext = ".jpg"
        if ext not in {".jpg", ".png", ".webp", ".gif", ".svg"}:
            ext = ".jpg"
        out_path = ext_dir / f"{digest}{ext}"
        rel_local = str(out_path.relative_to(ROOT)).replace("\\", "/")
        if out_path.exists() and out_path.stat().st_size > 100:
            mapping[url] = rel_local
            continue
        try:
            save_image(url, out_path, square_thumb=False)
            mapping[url] = rel_local
            print(f"Saved fallback: {rel_local}")
        except Exception as exc:
            print(f"  Fallback skip {url[:80]}...: {exc}")

    print("Updating HTML/CSS references...")
    changed = replace_urls_in_files(mapping)
    print(f"Updated {changed} files with local image paths.")

    print("Regenerating catalog and detail pages from JSON...")
    regenerate_pages()

    bad_files, external = verify_images()
    print(f"Verification: html_disguised_as_images={bad_files}, remaining_external_refs={external}")
    if bad_files or external:
        sys.exit(1)


if __name__ == "__main__":
    main()
