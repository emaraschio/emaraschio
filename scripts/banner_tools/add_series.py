#!/usr/bin/env python3
"""Add banners to the rotation, or move one that has not been shown yet.

    python3 scripts/banner_tools/add_series.py NEW.json
    python3 scripts/banner_tools/add_series.py NEW.json --on 2026-12-18
    python3 scripts/banner_tools/add_series.py --move cutaway/04-station-platform.webp --on 2026-12-18

NEW.json is a list of manifest entries ({file, style, theme, alt}). Entries up
to today's (day 0 is 2026-10-25, one a day, UTC) never move, so a banner
already shown keeps its day. Without --on the new entries are spread over the
rest of the rotation at even fractions (one new entry lands in the middle, not
at the end: a single banner added on 2026-11-14 first showed eight months
later). With --on they start on that day. Either way a new entry is nudged
forward when a neighbour has its style, and every entry after an insertion
shows one day later than before.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent.parent.parent / "banners" / "banners.json"
EPOCH = dt.date(2026, 10, 25)


def place(items: list, add: list, today: int, on: int | None = None) -> list:
    """The rotation with `add` in it. `today` and `on` are day indexes."""
    moving = {entry["file"] for entry in add}
    for index, item in enumerate(items):
        if item["file"] in moving and index <= today:
            sys.exit(f"banners/{item['file']} has already been shown (day {index}): it stays where it is")
    items = [item for item in items if item["file"] not in moving]
    head, tail = items[: today + 1], items[today + 1 :]
    n, m = len(tail), len(add)
    if on is not None:
        at = on - len(head)
        if not 0 <= at <= n:
            sys.exit(f"--on must be a day after today and no later than the end of the rotation ({EPOCH + dt.timedelta(days=len(items))})")
        out = tail[:at] + add + tail[at:]
    else:
        out, k = [], 0
        for i, item in enumerate(tail):
            out.append(item)
            # the k-th new entry goes (k + 1) / (m + 1) of the way through what is left
            while k < m and (i + 1) * (m + 1) >= (k + 1) * n:
                out.append(add[k])
                k += 1
        out.extend(add[k:])
    for _ in range(10):  # nudge same-style neighbours apart
        moved = False
        for i in range(1, len(out)):
            if out[i]["style"] == out[i - 1]["style"]:
                j = i + 1
                while j < len(out) and out[j]["style"] in (out[i]["style"], out[i - 1]["style"]):
                    j += 1
                if j < len(out):
                    out[i], out[j] = out[j], out[i]
                    moved = True
        if not moved:
            break
    result = head + out
    touching = [i for i in range(1, len(result)) if result[i]["style"] == result[i - 1]["style"]]
    if touching:
        sys.exit(f"two banners of one style would follow each other at day {touching[0]}: pick another day")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("new", nargs="?", help="JSON file with the entries to add")
    parser.add_argument("--move", metavar="FILE", help="an entry already in the manifest, by its file")
    parser.add_argument("--on", type=dt.date.fromisoformat, help="first day for the entries, YYYY-MM-DD")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    args = parser.parse_args()
    if bool(args.new) == bool(args.move):
        parser.error("give NEW.json or --move FILE, one of them")
    items = json.loads(args.manifest.read_text())
    if args.move:
        add = [item for item in items if item["file"] == args.move]
        if not add:
            sys.exit(f"banners.json has no banners/{args.move}")
        if args.on is None:
            parser.error("--move needs --on")
    else:
        add = json.loads(Path(args.new).read_text())
    today = (dt.datetime.now(dt.timezone.utc).date() - EPOCH).days
    result = place(items, add, today, None if args.on is None else (args.on - EPOCH).days)
    args.manifest.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    for entry in add:
        print(f"{EPOCH + dt.timedelta(days=result.index(entry))} {entry['file']}")
    print(f"{len(result)} entries, wraps {EPOCH + dt.timedelta(days=len(result))}")


if __name__ == "__main__":
    main()
