---
description: Run a fact-checked two-stage tournament over the whole active roster — fact-checkers verify each card once (cached), a judge ranks the field reading dossiers directly, then the top 3 fight head-to-head and a judge crowns a champion.
argument-hint: "(no arguments — always runs the whole active pool)"
allowed-tools: Task, Read, Write, Bash
---

# /judge-cards — the Card Arena (two-stage tournament)

Every ACTIVE card in `cards/` competes. Instead of an O(N²) round-robin (which
burns subagents and web calls fast), the field runs in two stages:

1. **Qualifier** — one judge reads every card's dossier + verdicts and ranks the
   whole field at once. **Top 3 advance**.
2. **Finals** — only the top 3 fight pairwise; one judge per pair scores the duel
   straight from both dossiers. Wins are tallied and a champion is crowned.

There is no file-picking — the roster is the field. To leave a card out, disable
it with `/list-cards disable <slug>`.

The debate has no advocate theater: there's nothing to argue, just dossiers and
verified facts, scored directly by a judge. This keeps the agent count low —
N fact-checkers + 1 ranking judge + up to 3 duel judges, not 3 agents per pair.

## Agent tiers
- **fact-checkers** (`card-fact-checker`) — one per ACTIVE card whose cached
  verdict is missing or stale. Uses WebSearch + WebFetch, ~95% confidence bar.
- **judge** (`card-judge`) — `MODE=rank` scores the whole qualifier field at once
  by reading every dossier directly; `MODE=duel` (default) scores a finals pair
  the same way. Discounts any claim not `VERIFIED` in the cached fact-check.

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
   - N ≤ 3 → skip the qualifier; every card is a finalist. Go straight to Step 3.
   - N > 12 → large field (up to N fact-checkers, all live web calls). Warn with
     N and ask to confirm before launching.

## Step 1 — fact-check each ACTIVE card ONCE, with a disk cache
Cache lives at `cards/.factcheck/<slug>.json`. For each active card:

1. Compute a hash of the dossier file (e.g. `shasum cards/<slug>.md`).
2. If `cards/.factcheck/<slug>.json` exists, its stored `dossier_hash` matches,
   and its `checked_at` is within 14 days → **reuse it**, no agent spawn. This is
   the single biggest cost cut: a re-run over an unchanged roster costs zero
   fact-checker calls.
3. Otherwise spawn `card-fact-checker` for that card (the rest can still run in
   parallel, in one message):
   - Task → `card-fact-checker`: `CARD_NAME=<card name>. DOSSIER_PATH=<card.md>.`
4. When a fact-checker returns, write its JSON to `cards/.factcheck/<slug>.json`
   with `dossier_hash` and `checked_at` (today's date) added, so the next run can
   reuse it.

Capture each card's verdict JSON (cached or freshly spawned) as `FACTCHECK_<slug>`
— reused in every later step.

## Step 2 — qualifier (rank the whole field, advance top 3)
Skip this step entirely if N ≤ 3 (all cards are finalists).

One `card-judge` call in `MODE=rank`, given every card's dossier path + cached
verdicts — it reads the dossiers itself, no per-card advocate statement needed:
- Task → `card-judge`: `MODE=rank. REQUIREMENTS_PATH=<RUBRIC>. CARDS=[{name, dossier_path, factcheck: FACTCHECK_slug}, ...all N].`

The **top 3** ranked cards are the finalists. Print the qualifier table:
```
  QUALIFIER — top 3 advance
  1. <card>  <score>
  2. <card>  <score>
  3. <card>  <score>
  (eliminated: <rest>, lowest first)
```

## Step 3 — finals (pairwise round-robin among the finalists)
For every unordered pair (A, B) of the ≤3 finalists, one judge call decides the
pair — no advocate openings/rebuttals:
- Task → `card-judge`: `MODE=duel. REQUIREMENTS_PATH=<RUBRIC>. CARD_A={name, dossier_path, factcheck: FACTCHECK_A}. CARD_B={name, dossier_path, factcheck: FACTCHECK_B}.`

All pairs in a single round can be spawned in parallel (one message, one Task
call per pair). Record the winner and both scores.

Print each final compactly, keeping any unverified-claim notes visible:
```
  <A> vs <B> → winner: <W>   (<A> <sa> / <B> <sb>)
```

## Step 4 — standings + champion
Tally finals wins. Print:
```
🏆 CARD ARENA — final standings
  1. <card>   <W> wins   (avg score <x>)
  2. <card>   <W> wins   ...
  CHAMPION: <most wins>   (ties broken by average judge score)
```
Note any unverified claims the judges flagged.

## Notes
- A game, not financial advice. Dossiers reflect terms captured June 2026.
- The official issuer page is the fact-checkers' highest-weight source; blogs and
  reviews only corroborate. Unverified claims survive but the judge discounts them.
- Disabled cards never appear here — that is intentional and silent.
- `cards/.factcheck/` is a cache, not a dossier — it's safe to delete to force a
  full re-verification, and safe to commit or gitignore either way.
