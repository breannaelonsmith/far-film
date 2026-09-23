"""far-film shot schema.

Axes are the contract. Vibe is not.
This module is the source of truth referenced by AGENTS.md.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping


AXES = (
    "shot_type",
    "lens_mm",
    "camera_move",
    "focal_subject",
    "depth_layering",
    "light_logic",
    "color_temp",
    "frame_rate",
    "aspect",
    "sound_design",
    "caption_density",
    "transition_type",
    "sequence_role",
    "source_discipline",
    "banned_motifs",
    "royalty_mode",
)

PRIMARY_AXES = (
    "shot_type",
    "lens_mm",
    "camera_move",
    "focal_subject",
    "light_logic",
    "color_temp",
    "aspect",
    "sequence_role",
)

BANNED_DEFAULT = (
    "house look",
    "make it cinematic",
    "cinematic vibe",
    "generic ai footage",
    "uncredited stock",
)

ALLOWED_SHOT_TYPES = (
    "ecu",
    "cu",
    "ms",
    "mws",
    "ws",
    "ews",
    "otc",
    "pov",
    "insert",
    "establishing",
    "two-shot",
    "over-shoulder",
    "tracking",
    "aerial",
)

ALLOWED_MOVES = (
    "static",
    "pan",
    "tilt",
    "dolly-in",
    "dolly-out",
    "truck",
    "crane",
    "handheld",
    "steadicam",
    "whip-pan",
    "zoom",
)

ALLOWED_ROLES = (
    "establish",
    "orient",
    "reveal",
    "beat",
    "reaction",
    "insert",
    "bridge",
    "climax",
    "release",
    "sting",
)


def canonical(axes: Mapping[str, Any]) -> str:
    """Deterministic serialization used for shot_id."""
    payload = {k: axes.get(k) for k in AXES}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def shot_id_from_axes(axes: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(canonical(axes).encode("utf-8")).hexdigest()
    return f"shot_{digest[:16]}"


@dataclass
class Shot:
    shot_id: str
    axes: dict[str, Any]
    variant_of: str | None = None
    sources: dict[str, str] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "shot_id": self.shot_id,
            "axes": self.axes,
            "variant_of": self.variant_of,
            "sources": self.sources,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Shot":
        return cls(
            shot_id=data["shot_id"],
            axes=dict(data.get("axes") or {}),
            variant_of=data.get("variant_of"),
            sources=dict(data.get("sources") or {}),
            notes=data.get("notes") or "",
        )


def normalize_axes(raw: Mapping[str, Any]) -> dict[str, Any]:
    axes: dict[str, Any] = {}
    for key in AXES:
        val = raw.get(key)
        if val is None:
            axes[key] = None
        elif key == "banned_motifs":
            if isinstance(val, str):
                axes[key] = [v.strip() for v in val.split(",") if v.strip()]
            else:
                axes[key] = list(val)
        elif key == "lens_mm":
            axes[key] = int(val) if val not in ("", None) else None
        elif key == "frame_rate":
            axes[key] = float(val) if val not in ("", None) else None
        else:
            axes[key] = val
    return axes


def compile_shot(
    raw_axes: Mapping[str, Any],
    *,
    variant_of: str | None = None,
    sources: Mapping[str, str] | None = None,
    notes: str = "",
) -> Shot:
    axes = normalize_axes(raw_axes)
    sid = shot_id_from_axes(axes)
    return Shot(
        shot_id=sid,
        axes=axes,
        variant_of=variant_of,
        sources=dict(sources or {}),
        notes=notes,
    )


class GateError(Exception):
    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        self.detail = detail
        super().__init__(f"{reason}: {detail}" if detail else reason)


def gate(
    shot: Shot | Mapping[str, Any] | None,
    *,
    known_parents: set[str] | None = None,
    asset_text: str = "",
) -> Shot:
    """Refuse naked assets. Enforce id == sha256(canonical(axes))."""
    if shot is None:
        raise GateError("no_shot", "naked asset refused")
    if not isinstance(shot, Shot):
        if not shot.get("shot_id"):
            raise GateError("no_shot", "naked asset refused")
        shot = Shot.from_dict(shot)

    if not shot.shot_id:
        raise GateError("no_shot", "naked asset refused")

    expected = shot_id_from_axes(shot.axes)
    if shot.shot_id != expected:
        raise GateError("id_mismatch", f"expected {expected}, got {shot.shot_id}")

    if shot.variant_of:
        parents = known_parents or set()
        if shot.variant_of not in parents:
            raise GateError("unknown_parent", shot.variant_of)

    banned = set(BANNED_DEFAULT)
    extra = shot.axes.get("banned_motifs") or []
    banned.update(str(x).lower() for x in extra)
    haystack = " ".join(
        [
            json.dumps(shot.axes, ensure_ascii=False).lower(),
            (shot.notes or "").lower(),
            (asset_text or "").lower(),
        ]
    )
    hits = [term for term in banned if term and term in haystack]
    # banned_motifs axis itself listing the terms is allowed; only refuse
    # when they appear as applied look language in notes/asset.
    applied = (shot.notes or "") + " " + (asset_text or "")
    applied_hits = [term for term in banned if term and term in applied.lower()]
    if applied_hits:
        raise GateError("banned_motifs", ", ".join(applied_hits))

    claims = []
    for key, val in shot.axes.items():
        if val not in (None, "", [], {}):
            claims.append(key)
    sources = shot.sources or {}
    discipline = (shot.axes.get("source_discipline") or "").lower()
    if discipline in ("strict", "required", "linked") and claims:
        missing = [c for c in claims if c not in sources and "axes" not in sources]
        # Allow a single catch-all source key "axes" or per-axis keys.
        if not sources and missing:
            raise GateError("source_discipline", f"unlinked claims: {missing}")

    return shot
