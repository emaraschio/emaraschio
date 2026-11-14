# Scripts

`rotate_banner.py` and `rotate_quote.py` are what the workflow runs (`.github/workflows/rotate-banner.yml`): they put today's banner and quote at the top of the README. `python3 scripts/rotate_banner.py --check` validates `banners/banners.json` against the files and writes nothing; `--date 2027-01-04` shows what a given day gets.

`banner_tools/` is how a banner is made. It is not run by the workflow.

## A new series of stills

1. **Generate.** One image per subject with `gpt-image-2.5-sunburst` on ElevenLabs: `quality: high`, `aspect_ratio: 3:1`, `resolution: 2K`, one generation each (184.5 credits). The master comes back at 2880x960. One generation per subject and no retry for taste: a subject is redone only when the image is wrong (unreadable, a broken figure, text where none was asked for).
2. **Look at every image** at full size before it goes anywhere. A contact sheet hides the broken ones.
3. **Convert.** `node scripts/banner_tools/to_banner.mjs master.png banners/<style>/<NN-name>.webp` writes an 1800x600 WebP under 400 KB.
4. **Place.** Write the entries (`file`, `style`, `theme`, `alt`) to a JSON file and run `python3 scripts/banner_tools/add_series.py new.json`. Banners already shown keep their day, the new ones are spread over the rest of the rotation, and no two of one style follow each other. `--on YYYY-MM-DD` puts them on a chosen day; `--move <file> --on YYYY-MM-DD` moves one that has not been shown yet.
5. **Check and commit.** `python3 scripts/rotate_banner.py --check`, then `docs(banner): ...`.

## Animating a banner

1. `node scripts/banner_tools/pad.mjs master.png padded.png` centers the 3:1 master on a 1920x1080 canvas, because the video model takes 16:9.
2. Kling 3 Pro, image to video: 5 seconds, 16:9, 1080p, no audio, with the padded still as both the first and the last frame so the loop closes (3,393 credits each).
3. `scripts/banner_tools/to_anim.sh render.mp4 banners/<style>/<NN-name>.webp` crops the band back out, scales it to 1800x600 at 15 fps and writes a looping WebP under 4 MB. Keep the image it replaces as `<NN-name>.still.webp` first.
4. `python3 scripts/banner_tools/animate_manifest.py <style>/<NN-name>` adds the `still` to the entry. The README then serves the still to readers who ask for reduced motion.

## What the tools need

- `to_banner.mjs` and `pad.mjs` borrow `sharp` from another checkout: `SHARP_FROM=/path/to/package.json`, by default a `maraschio.com` checkout next to this one.
- `to_anim.sh` needs `ffmpeg` and `img2webp` (libwebp). It writes frames and assembles them, so an ffmpeg built without the WebP encoder works.
- `python3 -m unittest discover -s scripts/banner_tools` tests the placement.
