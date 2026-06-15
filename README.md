# 🃏 Card Arena

Two AI agents fight over a prize: the right to be **the player's first credit card**.

Each agent is handed one card's dossier (a `.md` file under `cards/`) and told to
argue for it. Up front, a **fact-checker** agent verifies each card's numbers
against live web sources; those verdicts are handed to the advocates, who then
trade an opening statement and a few rebuttal rounds. A **judge** agent scores
both against the player's weighted requirements — discounting any claim that came
back unverified — and declares a winner.

This is a real multi-agent debate, not a templating trick — every line the
contestants and judge speak is a live Claude call.

## Two ways to play

| | Native slash command | Python CLI |
|---|---|---|
| How | `/judge-cards` inside Claude Code | `python -m arena` |
| Agents | 5 real Claude Code subagents (2 fact-checkers + 2 advocates + 1 judge), spawned in parallel waves | 1 Python process making sequential calls |
| Fact-checked | ✅ claims web-verified, `[UNVERIFIED]` discounted | ❌ unverified debate |
| Needs | Claude Code, web access for fact-checks | `claude` CLI on PATH, or an API key |
| Best for | "fact-checked parallel agents in my terminal" | scripting, tests, CI |

Both read the same `cards/` dossiers, but they are **not** equivalent: only the
native `/judge-cards` flow fact-checks each card against live web sources and has
the judge discount unverified claims. The Python CLI runs the debate straight from
the dossiers with no verification — it's the lightweight path for scripting and
tests, and it prints a reminder of this when it runs.

## Make it yours — build a player profile

The judge scores cards against a **player profile** (`cards/requirements.md`).
The one in the repo is a generic template. Build your own without editing files
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
stay on your machine and are never pushed. Point the arena at it:

```
/judge-cards cards/boa_student.md cards/discover_it_student.md personal/requirements.md
python -m arena --requirements personal/requirements.md
```

## The native version (nested, fact-checked agents)

Inside Claude Code, from the project root:

```
/judge-cards
/judge-cards cards/boa_student.md cards/discover_it_student.md cards/requirements.md
```

What happens:
0. **Round 0 — fact-check (once).** The command spawns two `card-fact-checker`
   subagents in parallel (WebSearch + WebFetch), one per card, to verify each
   card's numbers; claims that can't clear ~95% confidence are tagged
   `[UNVERIFIED]`. The verdicts are captured once and reused in both later rounds.
1. **Round 1 — parallel openings.** The command spawns two `card-advocate`
   subagents in one batch, each handed its card's verdicts; they argue blind,
   simultaneously.
2. **Round 2 — parallel rebuttals.** Both advocates run again in parallel, each
   handed the other's opening to rebut (and the same Round 0 verdicts).
3. **Round 3 — verdict.** One `card-judge` subagent reads the rubric and the full
   transcript, scores both — giving near-zero weight to `[UNVERIFIED]` claims —
   and declares a winner.

The flow is: command → 2 fact-checkers (once) → 2 advocates ×2 rounds → 1 judge.
The command orchestrates every subagent at the top level — advocates don't spawn
their own checkers — so verification happens once and the web isn't re-hit each
round.

Files: `.claude/commands/judge-cards.md`, `.claude/commands/build-profile.md`,
`.claude/agents/card-advocate.md`, `.claude/agents/card-fact-checker.md`,
`.claude/agents/card-judge.md`, `.claude/agents/profile-interviewer.md`.

## The pieces

```
card-arena/
├── .claude/
│   ├── commands/   ← /judge-cards (fact-checked debate), /build-profile (interview)
│   └── agents/     ← card-advocate, card-fact-checker, card-judge, profile-interviewer
├── cards/
│   ├── boa_student.md          ← contestant A dossier ("The Strategist")
│   ├── discover_it_student.md  ← contestant B dossier ("The Underdog")
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

## Run it

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
in plain English.

## Test it (no key required)

```bash
pip install pytest
pytest -q
```

The tests use a scripted fake model, so parsing, prompt-building, the full match
loop, and judge-JSON handling are all verified offline.

## Extend it (ideas)

- Add a third contestant and run a round-robin.
- Have the judge reveal a per-criterion score breakdown.
- Let the player (you) vote and compare against the judge.
- Add a `--seed`-able deterministic backend for reproducible demos.

---
*Not financial advice. The dossiers reflect terms captured June 2026; verify
live terms before applying to anything.*
