#!/usr/bin/env python3
"""Put this week's banner at the top of README.md.

The banners are listed in banners/banners.json. Week 0 starts on Monday
2026-10-26 and each Monday moves to the next banner, wrapping after the last,
so the order never jumps at a year boundary.

    python3 scripts/rotate_banner.py               # today (UTC)
    python3 scripts/rotate_banner.py --date 2027-01-04
    python3 scripts/rotate_banner.py --check       # validate only, write nothing
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
EPOCH = dt.date(2026, 10, 19)  # a Monday
START = "<!-- banner:start (set weekly by .github/workflows/rotate-banner.yml) -->"
END = "<!-- banner:end -->"


def load() -> list:
    items = json.loads(MANIFEST.read_text())
    if not items:
        sys.exit("banners.json is empty")
    for item in items:
        if not (BANNERS / item["file"]).is_file():
            sys.exit(f"banners.json names a missing file: banners/{item['file']}")
        if not item.get("alt", "").strip():
            sys.exit(f"banners/{item['file']} has no alt text")
    return items


def pick(items: list, day: dt.date) -> dict:
    return items[((day - EPOCH).days // 7) % len(items)]


def block(item: dict) -> str:
    alt = html.escape(item["alt"], quote=True)
    return f'{START}\n<img src="banners/{item["file"]}" alt="{alt}" width="100%">\n{END}'


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
