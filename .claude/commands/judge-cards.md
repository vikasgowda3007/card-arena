---
description: Run a fact-checked 3-tier credit-card debate — fact-checkers verify each card up front, advocates debate on those verdicts, a judge decides.
argument-hint: "[card-a.md] [card-b.md] [requirements.md]  (all optional)"
allowed-tools: Task, Read
---

# /judge-cards — the Card Arena (fact-checked)

Agents work together to award the prize: **the player's first credit card**. The
debate is fact-checked: each card's numbers are verified against live web sources
*before* any advocate argues them.

## Agent tiers
- **2 fact-checkers** (`card-fact-checker`) — YOU spawn one per card, up front.
  Each uses WebSearch + WebFetch to verify that card's claims at ~95% confidence
  and returns JSON verdicts.
- **2 advocates** (`card-advocate`) — argue for one card each, using the verdicts
  you hand them. They do NOT verify anything themselves (subagents can't reliably
  spawn subagents, and re-verifying every round wastes web calls).
- **1 judge** (`card-judge`) — scores both, discounting any `[UNVERIFIED]` claim.

Flow: this command → 2 fact-checkers (once) → 2 advocates ×2 rounds (fed the
verdicts) → 1 judge.

## Resolve inputs
- CARD_A  = `${1:-cards/boa_student.md}`
- CARD_B  = `${2:-cards/discover_it_student.md}`
- RUBRIC  = `${3:-cards/requirements.md}`

Read CARD_A and CARD_B yourself only to learn each card's `name` / `codename`
line. Do not read the rubric — that is the judge's job.

## Round 0 — fact-check both cards (TWO fact-checkers at once, ONCE)
In a SINGLE message, spawn BOTH fact-checkers in parallel. Capture each returned
JSON as `FACTCHECK_A` / `FACTCHECK_B` — you reuse these verdicts in every later
round, so this runs only once.

- Task → `card-fact-checker`: `DOSSIER_PATH=<CARD_A>.`
- Task → `card-fact-checker`: `DOSSIER_PATH=<CARD_B>.`

## Round 1 — parallel openings (TWO advocates at once)
In a SINGLE message, spawn BOTH advocates in parallel, each handed its card's
verdicts. Neither sees the other yet.

- Task → `card-advocate`: `PHASE=opening. DOSSIER_PATH=<CARD_A>. OPPONENT_NAME=<B name>. FACTCHECK=<FACTCHECK_A>.`
- Task → `card-advocate`: `PHASE=opening. DOSSIER_PATH=<CARD_B>. OPPONENT_NAME=<A name>. FACTCHECK=<FACTCHECK_B>.`

Print both openings under "Round 1 — Opening statements". Keep any `[UNVERIFIED]`
tags visible.

## Round 2 — parallel rebuttals (TWO advocates at once)
In a SINGLE message, spawn BOTH advocates again in parallel, each handed the
OTHER's opening AND the SAME verdicts from Round 0 (do not re-spawn fact-checkers):

- Task → `card-advocate`: `PHASE=rebuttal. DOSSIER_PATH=<CARD_A>. OPPONENT_NAME=<B name>. FACTCHECK=<FACTCHECK_A>. OPPONENT_OPENING="<B opening>".`
- Task → `card-advocate`: `PHASE=rebuttal. DOSSIER_PATH=<CARD_B>. OPPONENT_NAME=<A name>. FACTCHECK=<FACTCHECK_B>. OPPONENT_OPENING="<A opening>".`

Print both rebuttals under "Round 2 — Rebuttals".

## Round 3 — verdict (ONE judge)
- Task → `card-judge`: `REQUIREMENTS_PATH=<RUBRIC>. CARD_A_NAME=<...>. CARD_B_NAME=<...>. TRANSCRIPT=<all four statements>.`

## Final output
```
🃏 CARD ARENA — verdict
  <CARD_A_NAME>: <score>
  <CARD_B_NAME>: <score>
  WINNER: <winner>
  <reasoning>
```
Then list the judge's per-criterion breakdown and any unverified claims it noted.

## Notes
- A game, not financial advice. Dossiers reflect terms captured June 2026.
- The official issuer page is the fact-checkers' highest-weight source; blogs and
  reviews only corroborate. Unverified claims survive but the judge discounts them.
