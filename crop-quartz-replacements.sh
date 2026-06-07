#!/usr/bin/env bash
# Size all replacement PNGs to 1507x870: scale to COVER (fill frame), then center crop.
# Stone is always full-frame and visible. Use high-res source images to avoid blur.
set -e
QD="/Users/nilaabbasi/Stonesite/images/quartz"
TARGET_W=1507
TARGET_H=870

for f in "$QD"/cimento.png "$QD"/cumin.png "$QD"/grigio_scuro.png "$QD"/harvest_white.png \
         "$QD"/black_pearl.png "$QD"/sandy_beach.png "$QD"/terra_white.png "$QD"/venatino_beige.png \
         "$QD"/venatino_black.png "$QD"/venatino_grey.png "$QD"/venatino_white.png "$QD"/white_harvest.png; do
  [ ! -f "$f" ] && continue
  w=$(sips -g pixelWidth "$f" | awk '/pixelWidth:/{print $2}')
  h=$(sips -g pixelHeight "$f" | awk '/pixelHeight:/{print $2}')
  tmp="${f}.tmp.png"
  cp "$f" "$tmp"
  # Scale to COVER target (larger of the two ratios so image fills frame), then center crop
  scale_w=$(echo "scale=6; $TARGET_W / $w" | bc)
  scale_h=$(echo "scale=6; $TARGET_H / $h" | bc)
  larger_scale=$(echo "scale=6; if ($scale_w > $scale_h) $scale_w else $scale_h" | bc)
  new_w=$(printf "%.0f" "$(echo "scale=2; $w * $larger_scale" | bc)")
  new_h=$(printf "%.0f" "$(echo "scale=2; $h * $larger_scale" | bc)")
  [ "$new_w" -lt "$TARGET_W" ] && new_w=$TARGET_W
  [ "$new_h" -lt "$TARGET_H" ] && new_h=$TARGET_H
  left=$(echo "scale=0; ($new_w - $TARGET_W) / 2" | bc)
  top=$(echo "scale=0; ($new_h - $TARGET_H) / 2" | bc)
  sips -z "$new_h" "$new_w" "$tmp" --out "$tmp"
  sips -c "$TARGET_H" "$TARGET_W" --cropOffset "$top" "$left" "$tmp" --out "$f"
  rm -f "$tmp"
done
echo "Done sizing replacement images to ${TARGET_W}x${TARGET_H} (fill frame)"
