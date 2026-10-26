#!/usr/bin/env python3
"""Put the current quote under the banner in README.md.

The quotes are listed in quotes/quotes.json, in rotation order. Day 0 is
2026-10-26 and the quote moves on every day, wrapping after the last, the
same way scripts/rotate_banner.py walks the banners.

Each quote has "text" and either "author" or "own": true. Ezequiel's own
lines carry no name (it is his profile); "source" names the work a line comes
from and "url" links it (one of his essays, or where the source shows it).

    python3 scripts/rotate_quote.py               # today (UTC)
    python3 scripts/rotate_quote.py --date 2027-01-04
    python3 scripts/rotate_quote.py --check       # validate only, write nothing
"""

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
MANIFEST = ROOT / "quotes" / "quotes.json"
EPOCH = dt.date(2026, 10, 26)
PERIOD_DAYS = 1
START = "<!-- quote:start (rotated daily by .github/workflows/rotate-banner.yml) -->"
END = "<!-- quote:end -->"
DASHES = ("—", "–")


def load() -> list:
    items = json.loads(MANIFEST.read_text())
    if not items:
        sys.exit("quotes.json is empty")
    seen = set()
    for n, item in enumerate(items):
        text = item.get("text", "").strip()
        own = item.get("own") is True
        if not text or own == bool(item.get("author", "").strip()):
            sys.exit(f"quotes.json item {n} needs text and exactly one of author or own")
        if text in seen:
            sys.exit(f"quotes.json lists this quote twice: {text}")
        seen.add(text)
        for field in ("text", "author", "source"):
            if any(d in item.get(field, "") for d in DASHES):
                sys.exit(f"quotes.json item {n}: no em or en dash in {field}")
        if '"' in text:
            sys.exit(f"quotes.json item {n}: the text is quoted for you; use single quotes inside it")
        if item.get("url") and not item["url"].startswith("https://"):
            sys.exit(f"quotes.json item {n}: url must be https")
    return items


def pick(items: list, day: dt.date) -> dict:
    return items[((day - EPOCH).days // PERIOD_DAYS) % len(items)]


def attribution(item: dict) -> str:
    source = item.get("source", "").strip()
    if source and item.get("url"):
        source = f"[{source}]({item['url']})"
    parts = [p for p in (item.get("author", "").strip(), source) if p]
    return ", ".join(parts)


def block(item: dict) -> str:
    credit = attribution(item)
    line = f'> "{item["text"]}"' + (f" - {credit}" if credit else "")
    return f"{START}\n{line}\n{END}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", type=dt.date.fromisoformat, default=dt.datetime.now(dt.timezone.utc).date())
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    items = load()
    item = pick(items, args.date)
    text = README.read_text()
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        sys.exit("README.md needs exactly one quote block (start marker, then end marker)")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    new = head + block(item) + tail
    print(f"{args.date}: {item.get('author', 'own')}: {item['text'][:60]}")
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
