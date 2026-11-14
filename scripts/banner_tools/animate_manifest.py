#!/usr/bin/env python3
"""Mark banners as animated in banners/banners.json.

    python3 scripts/banner_tools/animate_manifest.py cutaway/01-five-workshops pixel/01-agent-org

For each name the entry's file stays <name>.webp (now the animation) and it
gains "still": "<name>.still.webp", the image it was before.
"""

import json
import sys
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent.parent.parent / "banners" / "banners.json"

names = sys.argv[1:]
if not names:
    sys.exit(__doc__)
items = json.loads(MANIFEST.read_text())
for name in names:
    entry = next((item for item in items if item["file"] == f"{name}.webp"), None)
    if entry is None:
        sys.exit(f"banners.json has no banners/{name}.webp")
    entry["still"] = f"{name}.still.webp"
MANIFEST.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n")
print("animated:", ", ".join(names))
