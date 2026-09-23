"""F1..F5 gate tests. Run: python -m pytest tests/test_gate.py -q
or: python tests/test_gate.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from sheet import GateError, compile_shot, gate, shot_id_from_axes  # noqa: E402


BASE = {
    "shot_type": "ms",
    "lens_mm": 50,
    "camera_move": "static",
    "focal_subject": "speaker",
    "depth_layering": "two-plane",
    "light_logic": "soft-overhead",
    "color_temp": "3200K",
    "frame_rate": 24,
    "aspect": "16:9",
    "sound_design": "dialogue-primary",
    "caption_density": "full",
    "transition_type": "cut",
    "sequence_role": "beat",
    "source_discipline": "linked",
    "banned_motifs": [],
    "royalty_mode": "original",
}


def test_f1_repro_id():
    a = compile_shot(BASE)
    b = compile_shot(dict(BASE))
    assert a.shot_id == b.shot_id
    other = dict(BASE)
    other["lens_mm"] = 35
    c = compile_shot(other)
    assert a.shot_id != c.shot_id


def test_f2_banned_terms_rejected():
    shot = compile_shot(BASE, notes="please make it cinematic")
    try:
        gate(shot, asset_text="cinematic vibe pass")
        raise AssertionError("expected GateError")
    except GateError as e:
        assert e.reason == "banned_motifs"


def test_f3_ids_survive_restart():
    shot = compile_shot(BASE, notes="hold", sources={"axes": "unit-test"})
    blob = json.dumps(shot.to_dict())
    restored = json.loads(blob)
    gated = gate(restored)
    assert gated.shot_id == shot.shot_id
    assert gated.shot_id == shot_id_from_axes(gated.axes)


def test_f4_different_settings_different_id():
    ids = set()
    for move in ("static", "dolly-in", "handheld"):
        axes = dict(BASE)
        axes["camera_move"] = move
        ids.add(compile_shot(axes).shot_id)
    assert len(ids) == 3


def test_f5_naked_prompt_refused():
    try:
        gate(None)
        raise AssertionError("expected no_shot")
    except GateError as e:
        assert e.reason == "no_shot"
    try:
        gate({"axes": BASE})  # no shot_id
        raise AssertionError("expected no_shot")
    except GateError as e:
        assert e.reason == "no_shot"


def main() -> int:
    tests = [
        test_f1_repro_id,
        test_f2_banned_terms_rejected,
        test_f3_ids_survive_restart,
        test_f4_different_settings_different_id,
        test_f5_naked_prompt_refused,
    ]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception as exc:
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
    print(f"{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
