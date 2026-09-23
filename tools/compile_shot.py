#!/usr/bin/env python3
"""Compile a shot YAML/JSON into a gated Shot packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# allow `python tools/compile_shot.py` from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sheet import compile_shot, gate  # noqa: E402


def _load(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError:
            # tiny subset parser: key: value lines, lists as [a, b]
            data: dict = {}
            current_list = None
            for raw in text.splitlines():
                line = raw.split("#", 1)[0].rstrip()
                if not line.strip():
                    continue
                if line.strip().startswith("- ") and current_list is not None:
                    data[current_list].append(line.strip()[2:].strip().strip('"'))
                    continue
                if ":" in line:
                    key, _, val = line.partition(":")
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if val == "":
                        current_list = key
                        data[key] = []
                    elif val.startswith("[") and val.endswith("]"):
                        inner = val[1:-1].strip()
                        data[key] = [x.strip().strip('"') for x in inner.split(",") if x.strip()]
                        current_list = None
                    else:
                        data[key] = val
                        current_list = None
            return data
        return yaml.safe_load(text) or {}
    return json.loads(text)


def main() -> int:
    p = argparse.ArgumentParser(description="Compile axes into a Shot packet")
    p.add_argument("path", type=Path, help="YAML or JSON axes file")
    p.add_argument("-o", "--out", type=Path, default=None)
    p.add_argument("--no-gate", action="store_true")
    args = p.parse_args()

    raw = _load(args.path)
    if not isinstance(raw, dict):
        raise SystemExit("could not parse shot file as a mapping")
    nested = raw.get("axes")
    if isinstance(nested, dict) and "shot_type" in nested:
        axes = nested
    else:
        axes = {k: v for k, v in raw.items() if k not in ("axes", "sources", "notes", "variant_of")}
    sources = raw.get("sources") or {}
    if not isinstance(sources, dict):
        sources = {"note": str(sources)}
    if isinstance(nested, str) and nested:
        sources.setdefault("note", nested)
    if raw.get("source_note"):
        sources.setdefault("note", raw["source_note"])
    shot = compile_shot(
        axes,
        variant_of=raw.get("variant_of"),
        sources=sources,
        notes=raw.get("notes") or "",
    )
    if not args.no_gate:
        shot = gate(shot)

    payload = json.dumps(shot.to_dict(), indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
