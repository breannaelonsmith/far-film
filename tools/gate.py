#!/usr/bin/env python3
"""Gate a compiled Shot JSON. Naked assets are refused."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sheet import GateError, Shot, gate  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Gate a Shot packet")
    p.add_argument("path", type=Path, help="compiled shot JSON")
    p.add_argument("--asset-text", default="", help="optional asset transcript/caption to scan")
    p.add_argument("--parent", action="append", default=[], help="known parent shot_id")
    args = p.parse_args()

    raw = json.loads(args.path.read_text(encoding="utf-8"))
    try:
        shot = gate(raw, known_parents=set(args.parent), asset_text=args.asset_text)
    except GateError as e:
        print(f"REFUSED {e.reason}" + (f" ({e.detail})" if e.detail else ""), file=sys.stderr)
        return 2
    print(f"OK {shot.shot_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
