---
description: Run a fact-checked 3-tier credit-card debate — advocates verify claims via fact-checkers, then debate, then a judge decides.
argument-hint: "[card-a.md] [card-b.md] [requirements.md]  (all optional)"
allowed-tools: Task, Read, WebSearch, WebFetch
---

# /judge-cards — the Card Arena (fact-checked)

Agents work together to award the prize: **the player's first credit card**. The
debate is fact-checked: every advocate must verify its numbers against live web
sources before arguing them.

## Agent tiers
- **2 advocates** (`card-advocate`) — argue for one card each.
- **2 fact-checkers** (`card-fact-checker`) — one spawned BY each advocate, uses
  WebSearch + WebFetch to verify that card's claims at ~95% confidence.
- **1 judge** (`card-judge`) — scores both, discounting any `[UNVERIFIED]` claim.

So the nesting is: this command → 2 advocates → each advocate → 1 fact-checker,
then → 1 judge. Agents launching agents.

## Resolve inputs
- CARD_A  = `${1:-cards/boa_student.md}`
- CARD_B  = `${2:-cards/discover_it_student.md}`
- RUBRIC  = `${3:-cards/requirements.md}`

Read CARD_A and CARD_B yourself only to learn each card's `name` / `codename`
line. Do not read the rubric — that is the judge's job.

## Round 1 — parallel openings (TWO advocates at once)
In a SINGLE message, spawn BOTH advocates with the Task tool so they run in
parallel. Each advocate will internally spawn its own fact-checker before it
speaks, so this round also runs the two fact-checkers.

- Task → `card-advocate`: `PHASE=opening. DOSSIER_PATH=<CARD_A>. OPPONENT_NAME=<B name>.`
- Task → `card-advocate`: `PHASE=opening. DOSSIER_PATH=<CARD_B>. OPPONENT_NAME=<A name>.`

Print both openings under "Round 1 — Opening statements". Keep any `[UNVERIFIED]`
tags visible.

## Round 2 — parallel rebuttals (TWO advocates at once)
In a SINGLE message, spawn BOTH advocates again in parallel, each handed the
OTHER's opening:

- Task → `card-advocate`: `PHASE=rebuttal. DOSSIER_PATH=<CARD_A>. OPPONENT_NAME=<B name>. OPPONENT_OPENING="<B opening>".`
- Task → `card-advocate`: `PHASE=rebuttal. DOSSIER_PATH=<CARD_B>. OPPONENT_NAME=<A name>. OPPONENT_OPENING="<A opening>".`

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
