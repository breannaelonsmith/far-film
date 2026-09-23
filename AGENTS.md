# AGENTS.md — (far-film repo)

> A shot is not a vibe.

This file is the contract. Every commit gate checks against it.
Every shot references it. Every test (F1..F5) reads it.

If you change the schema, update AGENTS.md first. The repo is downstream
of this file.

## What this repo is

shots, sequences, cuts, captions, color grades, storyboards, sound design, the film pipeline.

## Packet

```
shot  Shot | AssetRef
```

**No asset without `shot_id` + `hash`.** The gate refuses naked assets.

## Error this repo exists to stop

conflating every cut into one house look. 'Make it cinematic' is not an axis. Shot type, lens, and color temp are.

## Axes

film-pipeline axes: shot-type, lens-mm, camera-move, focal-subject, depth-layering, light-logic, color-temp, frame-rate, aspect, sound-design, caption-density, transition-type, sequence-role, source-discipline, banned-motifs, royalty-mode.

The schema is in the pipeline source (`tools/sheet.py`). Axes are the
contract; vibe is not.

## Surface

```python
shot.compile(axes) -> Shot
sequence.from_shots(shots)
cut.diff(a, b)
caption.from_shot(shot)
color.grade(shot, lut_ref)
```

## Gate

`commit_asset` defaults to `{gate}`. The gate checks:

1. `shot_id` is set.
2. `shot_id == sha256(canonical(axes))`.
3. `variant_of` (if set) is a known parent.
4. No banned-motifs present.
5. Source-discipline: every claim links to a source.

A naked shot (no `shot_id`) is refused with reason `no_shot`.

## Tests

| # | Test | What it checks |
|---|---|---|
| F1 | repro id | Shot with same axes -> same id; different axes -> different id. |
| F2 | banned terms rejected | Shot with banned-terms + asset containing them -> refused. |
| F3 | ids survive restart | Compile + serialize + deserialize -> all ids preserved. |
| F4 | two different settings cannot share id | Vary primary axes -> different id. |
| F5 | prompt without shot does not apply house | Naked prompt + gate -> refused, no fallback to default. |

## Anti-patterns

- house-look default
- vibe paragraphs without shot axes
- AI footage without source-discipline
- captions without a11y-contrast.

## Related

- the-far-queen/far-art (style substrate for color/LUT), the-far-queen/far-music (audio sync), the-far-queen/far-games (cutscene reuse)

## License

MIT. Free for all agents, human and non-human.
