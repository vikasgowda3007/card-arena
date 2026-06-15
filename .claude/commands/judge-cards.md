---
description: Run a 3-agent credit-card debate — two advocates argue in parallel, a judge decides.
argument-hint: "[card-a.md] [card-b.md] [requirements.md]  (all optional)"
allowed-tools: Task, Read
---

# /judge-cards — the Card Arena

Three agents work together to award the prize: **the player's first credit card**.
Two `card-advocate` subagents debate; one `card-judge` subagent decides.

## Resolve inputs
Use the arguments if given, else these defaults (paths are relative to the
project root):
- CARD_A  = `${1:-cards/boa_student.md}`
- CARD_B  = `${2:-cards/discover_it_student.md}`
- RUBRIC  = `${3:-cards/requirements.md}`

First, Read CARD_A and CARD_B yourself just to learn each card's `name` and
`codename` line (you need the names to label output and to tell each advocate
who the opponent is). Do not read the rubric — that is the judge's job.

## Round 1 — parallel openings  (TWO agents at once)
In a SINGLE message, spawn BOTH advocates with the Task tool so they run in
parallel. Neither sees the other yet.

- Task → subagent `card-advocate`:
  `PHASE=opening. DOSSIER_PATH=<CARD_A>. OPPONENT_NAME=<card B name>.`
- Task → subagent `card-advocate`:
  `PHASE=opening. DOSSIER_PATH=<CARD_B>. OPPONENT_NAME=<card A name>.`

Print both openings under a "Round 1 — Opening statements" heading.

## Round 2 — parallel rebuttals  (TWO agents at once)
In a SINGLE message, spawn BOTH advocates again in parallel, each handed the
OTHER's opening text:

- Task → `card-advocate`: `PHASE=rebuttal. DOSSIER_PATH=<CARD_A>.
  OPPONENT_NAME=<card B name>. OPPONENT_OPENING="<card B opening>".`
- Task → `card-advocate`: `PHASE=rebuttal. DOSSIER_PATH=<CARD_B>.
  OPPONENT_NAME=<card A name>. OPPONENT_OPENING="<card A opening>".`

Print both rebuttals under a "Round 2 — Rebuttals" heading.

## Round 3 — the verdict  (ONE judge agent)
Spawn the judge once:

- Task → subagent `card-judge`: `REQUIREMENTS_PATH=<RUBRIC>.
  CARD_A_NAME=<...>. CARD_B_NAME=<...>. TRANSCRIPT=<all four statements>.`

## Final output
Render the result as:

```
🃏 CARD ARENA — verdict
  <CARD_A_NAME>: <score>
  <CARD_B_NAME>: <score>
  WINNER: <winner>
  <reasoning>
```

Then list the per-criterion breakdown the judge returned, one line each.

## Notes
- This is a game, not financial advice. Dossiers reflect terms captured June 2026.
- Three agents truly run here: two advocates (twice, in parallel waves) and one
  judge. The parallelism is the two advocates within each round.
