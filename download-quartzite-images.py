#!/usr/bin/env python3
"""Download quartzite slab images, save as images/quartzite/{slug}.jpg, crop/resize to uniform square, update JSON."""
import json
import ssl
import urllib.request
from pathlib import Path

try:
    from PIL import Image
    import io
except ImportError:
    Image = None
    io = None

DATA = Path(__file__).parent.parent / "data" / "olympia-quartzite.json"
IMG_DIR = Path(__file__).parent.parent / "images" / "quartzite"
SIZE = 400  # uniform square side in pixels


def download_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
        return r.read()


def to_square(data, size=SIZE):
    """Crop center square and resize to size x size."""
    if not Image or not io:
        return None
    img = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    cropped = img.crop((left, top, left + side, top + side))
    return cropped.resize((size, size), Image.Resampling.LANCZOS)


def main():
    with open(DATA) as f:
        slabs = json.load(f)

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    ok = 0
    err = 0
    for s in slabs:
        slug = s.get("slug", "").strip()
        if not slug:
            continue
        url = s.get("img_large") or s.get("img_small", "")
        if not url or not url.startswith("http"):
            if s.get("img_small", "").startswith("images/"):
                ok += 1
            continue
        out_path = IMG_DIR / f"{slug}.jpg"
        try:
            raw = download_url(url)
            squared = to_square(raw)
            if squared is not None:
                squared.save(out_path, "JPEG", quality=88)
            else:
                out_path.write_bytes(raw)
            rel = f"images/quartzite/{slug}.jpg"
            s["img_small"] = rel
            s["img_large"] = rel
            ok += 1
        except Exception as e:
            print(f"  Skip {slug}: {e}")
            err += 1

    with open(DATA, "w") as f:
        json.dump(slabs, f, indent=2)

    print(f"Downloaded/saved {ok} quartzite images to {IMG_DIR} (uniform squares {SIZE}x{SIZE})")
    if err:
        print(f"Skipped {err} slabs due to errors.")


if __name__ == "__main__":
    main()
