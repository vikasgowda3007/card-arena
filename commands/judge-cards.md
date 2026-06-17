---
description: Run a fact-checked round-robin over the whole active roster — fact-checkers verify each card once, advocates debate every pair on those verdicts, a judge crowns a champion.
argument-hint: "(no arguments — always runs the whole active pool)"
allowed-tools: Task, Read
---

# /judge-cards — the Card Arena (whole-pool tournament)

Every ACTIVE card in `cards/` fights every other in a round-robin. Wins are
tallied and a champion is crowned. There is no file-picking — the roster is the
field. To leave a card out, disable it with `/list-cards disable <slug>`.

The debate is fact-checked: each card's numbers are verified against live web
sources **once, up front**, and those verdicts are reused in every matchup — no
card is ever re-verified.

## Agent tiers
- **N fact-checkers** (`card-fact-checker`) — YOU spawn one per ACTIVE card, up
  front. Each uses WebSearch + WebFetch to verify that card's claims at ~95%
  confidence and returns JSON verdicts. Cached and reused in every debate.
- **2 advocates per debate** (`card-advocate`) — argue for one card each, using
  the cached verdicts you hand them. They do NOT verify anything themselves
  (subagents can't reliably spawn subagents, and re-verifying every round wastes
  web calls).
- **1 judge per debate** (`card-judge`) — scores the pair, discounting any
  `[UNVERIFIED]` claim.

## Resolve the rubric
- RUBRIC = `personal/requirements.md` if it exists, else `cards/requirements.md`.

Prefer the personal profile when present (it's the real, gitignored one); fall
back to the public example template otherwise. Do not read the rubric yourself —
that is the judge's job. Just pass its path to each judge.

## Step 0 — build the ACTIVE field (honor the roster, skip silently)
1. List every `cards/*.md` except `requirements.md`.
2. Read `cards/roster.json` (if missing, treat all cards as active).
3. **Drop any card whose slug is `true` under `disabled`. Do this silently** — do
   not name, count, or mention disabled cards anywhere in the output.
4. Read each ACTIVE card's `name` / `codename` line.
5. Let N = number of ACTIVE cards.
   - N < 2 → tell the player to add or enable cards (`/scout-cards` or
     `/list-cards enable <slug>`), then stop.
   - N > 6 → large tournament (N×(N−1)/2 debates, each several subagents + live
     web calls). Warn with the debate count and ask to confirm before launching.

## Step 1 — fact-check each ACTIVE card ONCE (cache)
In a SINGLE message, spawn ALL fact-checkers in parallel — one per active card.
Capture each returned JSON as `FACTCHECK_<slug>`. You reuse these verdicts in
every later debate, so this runs only once per card.

- Task → `card-fact-checker`: `CARD_NAME=<card name>. DOSSIER_PATH=<card.md>.`
  (one per active card)

## Step 2 — round-robin debates
For every unordered pair (A, B) of ACTIVE cards:

1. **Openings (parallel):** in a SINGLE message spawn BOTH advocates,
   `PHASE=opening`, each handed its dossier, the opponent name, and its cached
   verdicts. Neither sees the other yet.
   - Task → `card-advocate`: `PHASE=opening. DOSSIER_PATH=<A>. OPPONENT_NAME=<B name>. FACTCHECK=<FACTCHECK_A>.`
   - Task → `card-advocate`: `PHASE=opening. DOSSIER_PATH=<B>. OPPONENT_NAME=<A name>. FACTCHECK=<FACTCHECK_B>.`
2. **Rebuttals (parallel):** in a SINGLE message spawn BOTH again,
   `PHASE=rebuttal`, each handed the OTHER's opening AND the SAME cached verdicts.
   - Task → `card-advocate`: `PHASE=rebuttal. DOSSIER_PATH=<A>. OPPONENT_NAME=<B name>. FACTCHECK=<FACTCHECK_A>. OPPONENT_OPENING="<B opening>".`
   - Task → `card-advocate`: `PHASE=rebuttal. DOSSIER_PATH=<B>. OPPONENT_NAME=<A name>. FACTCHECK=<FACTCHECK_B>. OPPONENT_OPENING="<A opening>".`
3. **Verdict:** one `card-judge` with the rubric + four statements. Record the
   winner and both scores.
   - Task → `card-judge`: `REQUIREMENTS_PATH=<RUBRIC>. CARD_A_NAME=<A>. CARD_B_NAME=<B>. TRANSCRIPT=<all four statements>.`

Print each debate compactly, keeping any `[UNVERIFIED]` tags visible:
```
  <A> vs <B> → winner: <W>   (<A> <sa> / <B> <sb>)
```

## Step 3 — standings + champion
Tally wins. Print:
```
🏆 CARD ARENA — final standings
  1. <card>   <W> wins   (avg score <x>)
  2. <card>   <W> wins   ...
  CHAMPION: <most wins>   (ties broken by average judge score)
```
Note any `[UNVERIFIED]` claims the judges flagged.

## Notes
- A game, not financial advice. Dossiers reflect terms captured June 2026.
- The official issuer page is the fact-checkers' highest-weight source; blogs and
  reviews only corroborate. Unverified claims survive but the judge discounts them.
- Disabled cards never appear here — that is intentional and silent.
