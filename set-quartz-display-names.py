#!/usr/bin/env python3
"""Set correct display names for quartz slabs. Keeps slugs/images unchanged."""
import json
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "olympia-quartz.json"

# Slug -> correct display name (from site/product names)
SLUG_TO_NAME = {
    "b_carrara_j": "Bianco Carrara",
    "cal_cla_j": "Calacatta Classico",
    "cal_primo_j": "Calacatta Primo",
    "carr_mist": "Carrara Mist",
    "carr_gold_j": "Carrara Gold",
    "c_grey_j2cm_mt": "Concrete Grey",
    "026_jsl": "Cimento",
    "ptr_grey_lt_j": "Grey Shimmer",
    "ptr_grey_j": "Pietre Grey",
    "nro_marq_j": "Nero Marquina",
    "statuario_ven_j": "Statuario Venato",
    "statuario_cla_j": "Statuario Classico",
    "v209_jsl": "Cyrus Grey",
    "008_jsl": "Cumin",
    "014_jsl": "Grigio Scuro",
    "007_jsl": "Sandy Beach",
    "012_jsl": "Harvest White",
    "001_jsl": "Super White",
    "v207_jsl": "Terra White",
    "v101_jsl": "Venatino Beige",
    "v210_jsl": "Venatino Grey",
    "009_jsl": "Venatino White",
    "013_jsl": "Venatino Black",
    "027_jsl": "Black Pearl",
    "60cm_x_60cm_x_1": "White Harvest",
}


def main():
    with open(DATA) as f:
        slabs = json.load(f)

    for s in slabs:
        slug = s.get("slug", "")
        if slug in SLUG_TO_NAME:
            s["name"] = SLUG_TO_NAME[slug]

    with open(DATA, "w") as f:
        json.dump(slabs, f, indent=2)

    print(f"Updated {len([s for s in slabs if s.get('slug') in SLUG_TO_NAME])} quartz display names in {DATA}")


if __name__ == "__main__":
    main()
