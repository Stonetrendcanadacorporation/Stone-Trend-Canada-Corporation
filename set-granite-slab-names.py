#!/usr/bin/env python3
"""Set granite slab names from the canonical list. Tiles are left unchanged."""
import json
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "olympia-granite.json"

# Slug -> exact display name (slabs only; from canonical list). Variants (lf, sc, fl, 2cmhd) get descriptive names.
SLAB_NAMES = {
    "agata": "Agata",
    "ambra_blue": "Ambra Blue",
    "astrius": "Astrius",
    "azurite": "Azurite",
    "basalt": "Basaltina",
    "belvedere": "Belvedere",
    "bianco_antico": "Bianco Antico",
    "bia_col": "Bianco Colorado",
    "aspen_white": "Aspen White",
    "alaska_white": "Alaska White",
    "alp_white": "Alpha White",
    "azul_plat": "Azul Platino",
    "blu_bahia": "Blue Bahia",
    "brown_romano": "Branco Romano",
    "a_brown": "Antique Brown",
    "bbk_brown": "Bainbrook Brown",
    "baltic_bwn": "Baltic Brown",
    "cale_bwn": "Caledonia Brown",
    "coff_bwn": "Coffee Brown",
    "col_white": "Colonial White",
    "cor_bwn": "Coral Brown",
    "cor_gold": "Coral Gold",
    "azul_coast": "Azul Coast",
    "del_white": "Delicatus White",
    "desert_bwn": "Desert Brown",
    "dueto": "Dueto",
    "el_bwm": "Elegant Brown",
    "ever_white": "Everest White",
    "black_fan": "Black Fantasy",
    "dia_arr": "Diamond Arrow",
    "fusion": "Fusion",
    "gal_blue": "Galattica Blue",
    "black_galaxy": "Black Galaxy",
    "g_ornam": "Giallo Ornamentale",
    "g_vicenza": "Giallo Vicenza",
    "grg_sardo": "Grigio Sardo",
    "hima_white": "Himalaya White",
    "ice_brown": "Ice Brown",
    "illusion": "Illusion",
    "imp_coffee": "Imperial Coffee",
    "came_ivo": "Camelot Ivory",
    "kod_bwn": "Kodiak Brown",
    "lab_an_black": "Labrador Angolo",
    "lennon": "Lennon",
    "luna_prl": "Luna Pearl",
    "black_mar": "Black Marinace",
    "mos_cri": "Moscavita",
    "negresco": "Negresco",
    "nero_galas": "Nero Galassia",
    "nro_impala": "Nero Impala",
    "net_bord": "Netuno Bordeaux",
    "nia_gold": "Niagara Gold",
    "ab_black": "Black",
    "am_black": "American Black",
    "cam_black": "Cambrian Black",
    "new_caled": "New Caledonia",
    "mis_nig": "Misty Night",
    "n_ven_gold": "New Venetian Gold",
    "patagonia": "Patagonia",
    "blu_pearl": "Blue Pearl",
    "black_pearl": "Black Pearl",
    "roma_imp": "Roma Imperiale",
    "saph_blu": "Sapphire Blue",
    "serenata": "Serenata",
    "sib_white": "Siberian White",
    "sil_beach": "Silver Beach",
    "sil_cloud": "Silver Cloud",
    "sil_grey": "Silver Grey",
    "st_cecilia": "St. Cecilia",
    "st_grey": "Steel Grey",
    "super_white": "Super White",
    "tan_brown": "Tan Brown",
    "titanium": "Titanium",
    "trop_bwn": "Tropical Brown",
    "trop_white": "Tropical White",
    "typh_bord": "Typhoon Bordeaux",
    "valley_white": "Valley White",
    "verde_bah": "Verde Bahia",
    "peacock": "Peacock Green",
    "via_lattea": "Via Lattea",
    "white_torr": "White Torroncino",
    # Variant slugs (LF, SC, FL, 2cmhd) – keep descriptive
    "cam_black_fl": "Cambrian Black Flamed",
    "ab_black_2cmhd": "Black 2cm",
    "belved_lf": "Belvedere Leather",
    "a_brown_lf": "Antique Brown Leather",
    "matrix_lf": "Matrix",
    "ab_black_lf": "Black Leather",
    "mis_nig_lf": "Misty Night Leather",
    "taj_mah_lf": "Taj Mahal",
    "via_latt_lf": "Via Lattea Leather",
    "ang_black_sc": "Angola Black",
    "matrix_sc": "Matrix SC",
}


def main():
    with open(DATA) as f:
        items = json.load(f)
    updated = 0
    for item in items:
        if item.get("format") != "slab":
            continue
        slug = item.get("slug", "")
        if slug in SLAB_NAMES:
            new_name = SLAB_NAMES[slug]
            if item.get("name") != new_name:
                item["name"] = new_name
                updated += 1
    with open(DATA, "w") as f:
        json.dump(items, f, indent=2)
    print(f"Updated {updated} slab names in {DATA}")


if __name__ == "__main__":
    main()
