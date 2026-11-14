#!/bin/bash
# to_anim.sh <in.mp4> <out.webp>: crop the 1920x640 band out of the 16:9 render, scale to 1800x600,
# 15 fps frames through ffmpeg, then img2webp into a looping WebP; quality stepped down until under 4 MB.
set -euo pipefail
in="$1"; out="$2"
tmp="$(mktemp -d)"
ffmpeg -nostdin -v error -y -i "$in" -vf "crop=1920:640:0:220,scale=1800:600:flags=lanczos,fps=15" "$tmp/f%03d.png"
n=$(ls "$tmp" | wc -l | tr -d ' ')
for q in 75 68 60 52; do
  img2webp -loop 0 -d 67 -lossy -q "$q" -m 6 "$tmp"/f*.png -o "$out" >/dev/null 2>&1
  kb=$(( $(stat -f%z "$out") / 1024 ))
  if [ "$kb" -le 4096 ]; then echo "$out $n frames ${kb} KB q$q"; rm -rf "$tmp"; exit 0; fi
done
rm -rf "$tmp"; echo "$out still over 4 MB at q52"; exit 1
