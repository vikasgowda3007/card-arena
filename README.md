# 🃏 Card Arena

AI agents fight over a prize: the right to be **the player's first credit card**.

Every card lives as a dossier (a `.md` file under `cards/`). In the native flow,
the whole active roster plays a **round-robin tournament** — each card debates
every other, wins are tallied, and a champion is crowned. Up front, a
**fact-checker** agent verifies each card's numbers against live web sources (once
per card, then cached); those verdicts are handed to the advocates, who trade an
opening statement and a rebuttal. A **judge** agent scores each pair against the
player's weighted requirements — discounting any claim that came back unverified.

This is a real multi-agent debate, not a templating trick — every line the
contestants and judge speak is a live Claude call.

## Install

Card Arena is a Claude Code plugin. The repo is its own marketplace, so:

```
/plugin marketplace add vikasgowda3007/card-arena
/plugin install card-arena@card-arena
```

That gives you `/arena`, `/build-profile`, `/judge-cards`, `/scout-cards`, and
`/list-cards` in any project. The `arena/` Python CLI is a separate, optional
path (clone the repo and run `python -m arena`); it isn't part of the plugin.

## The commands

| Command | What it does |
|---|---|
| `/arena` | Front door. Run with no argument for a menu; dispatches to all of the below. |
| `/arena profile` (or `/build-profile`) | Interview yourself into a weighted rubric (see below). |
| `/judge-cards` (or `/arena battle`) | Round-robin tournament over the whole **active** roster; crowns a champion. |
| `/scout-cards [n]` (or `/arena scout n`) | Discover `n` profile-matched cards on the web, fact-check them, add verified dossiers to `cards/`. |
| `/list-cards` (or `/arena list`) | Show the roster; `enable`/`disable <slug>` to bench a card without deleting it. |

The roster *is* the field — `/judge-cards` takes no card arguments. To leave a
card out of a tournament, bench it with `/list-cards disable <slug>`; disabled
cards are silently skipped (their dossiers stay on disk). Above 6 active cards the
tournament warns you of the debate count before launching.

## Make it yours — build a player profile

The judge scores cards against a **player profile**. The repo ships a generic
example template at `cards/requirements.md`. Build your own without editing files
by hand:

```
/build-profile            inside Claude Code
```

This runs a short adaptive interview. A separate `profile-interviewer` agent
listens to every answer, decides which angles are still missing (credit history,
spending shape, fee tolerance, goal, approval constraints), and feeds the next
questions back to you — so you're only ever asked what actually matters. When the
picture is complete it writes a weighted rubric to `personal/requirements.md`.

`personal/` is **gitignored**, so your real profile, spending habits, and verdicts
stay on your machine and are never pushed. The slash commands prefer it
automatically: `/judge-cards` and `/scout-cards` use `personal/requirements.md`
when it exists and fall back to the public `cards/requirements.md` template
otherwise. The Python CLI takes it explicitly:

```
python -m arena --requirements personal/requirements.md
```

## The native version (nested, fact-checked agents)

`/judge-cards` (or `/arena battle`) runs the tournament:

0. **Build the field.** List `cards/*.md`, read `cards/roster.json`, drop disabled
   cards silently. N active cards → N×(N−1)/2 debates.
1. **Fact-check once per card.** The command spawns one `card-fact-checker`
   subagent per active card in parallel (WebSearch + WebFetch); claims that can't
   clear ~95% confidence are tagged `[UNVERIFIED]`. Each card's verdict is cached
   and reused in every matchup — the web is never re-hit for the same card.
2. **Round-robin debates.** For each pair: two `card-advocate` subagents argue in
   parallel (openings blind, then rebuttals on each other's openings), each handed
   its card's cached verdicts. One `card-judge` scores the pair, giving near-zero
   weight to `[UNVERIFIED]` claims, and records the winner.
3. **Standings.** Wins are tallied and a champion crowned (ties broken by average
   judge score).

The command orchestrates every subagent at the top level — advocates don't spawn
their own checkers — so verification happens once per card and the web isn't
re-hit each round.

`/scout-cards` grows the field instead of fighting: a `card-scout` agent reads
your profile, searches the web for matching cards, drops any that fail your
rubric's hard filters or already exist, verifies each survivor with a
`card-fact-checker`, and writes a verified dossier per survivor into `cards/`.

Files: everything under `commands/` and `agents/`.

## The pieces

```
card-arena/
├── .claude-plugin/
│   ├── plugin.json      ← plugin manifest (name, version, description)
│   └── marketplace.json ← makes this repo its own installable marketplace
├── commands/      ← /arena, /build-profile, /judge-cards, /scout-cards, /list-cards
├── agents/        ← card-advocate, card-fact-checker, card-judge, card-scout, profile-interviewer
├── cards/
│   ├── boa_student.md          ← contestant dossier ("The Strategist")
│   ├── discover_it_student.md  ← contestant dossier ("The Underdog")
│   ├── roster.json             ← active/disabled registry (a card is active unless listed)
│   └── requirements.md         ← the prize + weighted rubric template (judge reads this)
├── personal/       ← gitignored: your real profile + verdicts, never published
├── arena/
│   ├── dossier.py   ← parse a card .md into a Card
│   ├── llm.py       ← model backend (Claude CLI → API key → fail loudly)
│   ├── agents.py    ← ContestantAgent, JudgeAgent, prompt builders
│   ├── arena.py     ← orchestrates opening → rebuttals → verdict
│   └── cli.py       ← `python -m arena`
└── tests/           ← run with NO model, using a fake LLM
```

## The Python CLI (lightweight, pairwise, unverified)

The native slash flow is the full experience: fact-checked, parallel agents, a
whole-roster tournament. The Python CLI is the **lightweight path for scripting
and tests** — it runs a single pairwise debate straight from two dossiers with
**no web verification**, and prints a reminder of that when it runs.

If you run this **inside the Claude CLI**, the `claude` command is on PATH —
that's the default backend, no API key needed:

```bash
cd card-arena
python -m arena                 # BofA vs Discover, 2 rebuttal rounds
python -m arena --rounds 3
python -m arena --backend cli   # force the claude CLI backend
```

Prefer the API instead? `export ANTHROPIC_API_KEY=sk-ant-...` and add
`--backend api`. If neither backend is available the program tells you exactly
what to do rather than faking output.

### Preview without spending a call

```bash
python -m arena --dry-run       # prints the matchup + a sample agent prompt
```

### Swap the contestants

Any `.md` works as a dossier — point at your own:

```bash
python -m arena --card-a cards/boa_student.md \
                --card-b cards/my_other_card.md \
                --requirements cards/requirements.md
```

A dossier just needs a `# Title` and ideally `- name:` / `- codename:` lines;
the agent reads the whole file as prose, so write its strengths and weaknesses
in plain English. (Or let `/scout-cards` write them for you.)

## Test it (no key required)

```bash
pip install pytest
pytest -q
```

The tests use a scripted fake model, so parsing, prompt-building, the full match
loop, and judge-JSON handling are all verified offline.

## Extend it (ideas)

- Have the judge reveal a per-criterion score breakdown.
- Let the player (you) vote and compare against the judge.
- Add a `--seed`-able deterministic backend for reproducible demos.
- Teach the Python CLI to run the whole-roster round-robin too.

---
*Not financial advice. The dossiers reflect terms captured June 2026; verify
live terms before applying to anything.*
