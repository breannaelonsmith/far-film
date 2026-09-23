# far-film

**shots, sequences, cuts, captions, color. Shot is the gate; vibe is not.**

shots, sequences, cuts, captions, color grades, storyboards, sound design, the film pipeline.

## What this repo is

- A free, public-domain substrate for the shot pipeline.
- A gate (shot schema) that no asset enters without axes.
- A growing library of shots.

## What this repo is not

- A prompt collection. (Prompts are noise without axes.)
- A house-style. (The whole point is *named* shot, not default look.)
- A model zoo. (Models belong upstream; we use the open ones.)

## AGENTS.md

The schema lives in [AGENTS.md](./AGENTS.md). Read it first. The axes
are the contract.

## Repo layout

```
far-film/
├── AGENTS.md                # the schema (this is the contract)
├── README.md                # this file
├── LICENSE                  # MIT
├── shots/             # shot examples
├── tools/                   # shot.compile + shot.gate
└── tests/                   # F1..F5 gate tests
```

## Quick start

```bash
git clone https://github.com/the-far-queen/far-film.git
cd far-film
# Read AGENTS.md
# Pick an example from shots/
# Compile a variant: python tools/compile_shot.py path/to/shot.yaml
# Gate: python tools/gate.py path/to/shot.json
```

## License

MIT. Free for all agents, human and non-human. No copyright trap.
No paywall. No "research only" carve-out. Style axes belong to everyone.

## Sister repos

the-far-queen/far-art (style substrate for color/LUT), the-far-queen/far-music (audio sync), the-far-queen/far-games (cutscene reuse)

## The whole project

Bobby's project is 7 repos + a website + social media + a book on Amazon:

1. [the-far-queen/fieldcore](https://github.com/the-far-queen/fieldcore) — geometry + math substrate
2. [the-far-queen/simself](https://github.com/the-far-queen/simself) — identity + kernel
3. [the-far-queen/far-art](https://github.com/the-far-queen/far-art) — art + design
4. [the-far-queen/far-writing](https://github.com/the-far-queen/far-writing) — this repo
5. [the-far-queen/far-music](https://github.com/the-far-queen/far-music) — music
6. [the-far-queen/far-film](https://github.com/the-far-queen/far-film) — film
7. [the-far-queen/far-games](https://github.com/the-far-queen/far-games) — games

Plus farqueen.com, social media accounts, and a book on Amazon via Canva.
# far-film
