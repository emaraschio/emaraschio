#!/usr/bin/env python3
"""Put the current banner at the top of README.md.

The banners are listed in banners/banners.json, in rotation order. Day 0 is
2026-10-25 and the banner moves on every PERIOD_DAYS days, wrapping after the
last, so the order never jumps at a month or year boundary.

    python3 scripts/rotate_banner.py               # today (UTC)
    python3 scripts/rotate_banner.py --date 2027-01-04
    python3 scripts/rotate_banner.py --check       # validate only, write nothing

An entry may be animated. Then "file" is the animated WebP and "still" names
a still WebP of the same scene; the README gets a <picture> that serves the
still to readers who ask for reduced motion (prefers-reduced-motion: reduce)
and the animation to everyone else. The <img> stays on its own line so the
workflow's commit message still finds the banner path.
"""

import argparse
import datetime as dt
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
BANNERS = ROOT / "banners"
MANIFEST = BANNERS / "banners.json"
EPOCH = dt.date(2026, 10, 25)
PERIOD_DAYS = 1
START = "<!-- banner:start (rotated daily by .github/workflows/rotate-banner.yml) -->"
END = "<!-- banner:end -->"


def load() -> list:
    items = json.loads(MANIFEST.read_text())
    if not items:
        sys.exit("banners.json is empty")
    seen = set()
    for item in items:
        if item["file"] in seen:
            sys.exit(f"banners.json lists banners/{item['file']} twice")
        seen.add(item["file"])
        if not (BANNERS / item["file"]).is_file():
            sys.exit(f"banners.json names a missing file: banners/{item['file']}")
        if not item.get("alt", "").strip():
            sys.exit(f"banners/{item['file']} has no alt text")
        still = item.get("still")
        if still is not None:
            if not (BANNERS / still).is_file():
                sys.exit(f"banners.json names a missing still: banners/{still}")
            if still in seen or still == item["file"]:
                sys.exit(f"banners.json lists banners/{still} twice")
            seen.add(still)
    on_disk = {str(p.relative_to(BANNERS)) for p in BANNERS.rglob("*.webp")}
    if on_disk - seen:
        sys.exit(f"images not in banners.json: {', '.join(sorted(on_disk - seen))}")
    return items


def pick(items: list, day: dt.date) -> dict:
    return items[((day - EPOCH).days // PERIOD_DAYS) % len(items)]


def block(item: dict) -> str:
    alt = html.escape(item["alt"], quote=True)
    img = f'<img src="banners/{item["file"]}" alt="{alt}" width="100%">'
    if not item.get("still"):
        return f"{START}\n{img}\n{END}"
    source = f'<source media="(prefers-reduced-motion: reduce)" srcset="banners/{item["still"]}">'
    return f"{START}\n<picture>\n{source}\n{img}\n</picture>\n{END}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", type=dt.date.fromisoformat, default=dt.datetime.now(dt.timezone.utc).date())
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    items = load()
    item = pick(items, args.date)
    text = README.read_text()
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        sys.exit("README.md needs exactly one banner block (start marker, then end marker)")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    new = head + block(item) + tail
    print(f"{args.date}: {item['file']}")
    if args.check:
        return 0
    if new != text:
        README.write_text(new)
        print("README.md updated")
    else:
        print("README.md already shows it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
