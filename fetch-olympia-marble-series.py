#!/usr/bin/env python3
"""Fetch marble products from Olympia Tile marble series (olympiatile.com) via GraphQL."""
import json
import re
import ssl
import urllib.request
from pathlib import Path


GRAPHQL_URL = "https://www.olympiatile.com/graphql"
MARBLE_SERIES_URL = "https://www.olympiatile.com/en/marble-series.html"

QUERY = """
{
  products(filter: { sku: { eq: "MARBLE" } }) {
    items {
      name
      sku
      url_key
      ... on ConfigurableProduct {
        variants {
          product {
            sku
            name
            image { url }
          }
        }
      }
    }
  }
}
"""


def fetch_graphql():
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=json.dumps({"query": QUERY}).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return json.loads(r.read().decode("utf-8"))


def slugify(name):
    s = re.sub(r"[^a-zA-Z0-9\s]", "", name.lower())
    return re.sub(r"\s+", "_", s.strip())


def extract_marble_type(variant_name):
    """Extract marble type from 'MARBLE - BIANCO CARRARA' -> 'Bianco Carrara'."""
    if not variant_name or "MARBLE - " not in variant_name.upper():
        return None
    part = variant_name.split(" - ", 1)[-1].strip()
    # Clean up: USER-DEFINED, UNKNOWN, PENCIL RAIL etc.
    if part.upper() in ("USER-DEFINED", "UNKNOWN"):
        return None
    if "PENCIL RAIL" in part.upper():
        return None
    # Title case
    return part.title()


def main():
    print("Fetching marble series from GraphQL...")
    data = fetch_graphql()
    items = data.get("data", {}).get("products", {}).get("items", [])
    if not items:
        print("No products found")
        return

    variants = items[0].get("variants", [])
    print(f"Found {len(variants)} variants")

    # Deduplicate by marble type, keep best image (non-placeholder)
    by_type = {}
    placeholder = "placeholder/image.jpg"

    for v in variants:
        p = v.get("product", {})
        name = p.get("name", "")
        marble_type = extract_marble_type(name)
        if not marble_type:
            continue
        img = (p.get("image") or {}).get("url", "")
        sku = p.get("sku", "")

        if marble_type not in by_type or (
            placeholder in img.lower() and placeholder not in (by_type[marble_type].get("img_large") or "").lower()
        ):
            if marble_type not in by_type or placeholder not in img.lower():
                by_type[marble_type] = {
                    "name": marble_type,
                    "code": sku,
                    "thickness": None,
                    "img_small": img if img else None,
                    "img_large": img if img else None,
                    "slug": slugify(marble_type) + "_tile",
                    "url": MARBLE_SERIES_URL,
                    "format": "tile",
                }

    results = list(by_type.values())
    print(f"Extracted {len(results)} unique marble types")

    # Load existing slab data and merge
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    existing_path = data_dir / "olympia-marble.json"
    existing = []
    if existing_path.exists():
        with open(existing_path) as f:
            existing = json.load(f)
        existing_slugs = {s.get("slug") for s in existing}
        # Ensure unique slugs for tile entries
        for r in results:
            base = r["slug"]
            while r["slug"] in existing_slugs:
                r["slug"] = base + "_" + str(len(existing_slugs))
                existing_slugs.add(r["slug"])
            existing_slugs.add(r["slug"])

    merged = existing + results
    with open(existing_path, "w") as f:
        json.dump(merged, f, indent=2)
    print(f"Saved {len(merged)} total marbles to {existing_path}")


if __name__ == "__main__":
    main()
