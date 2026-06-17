---
description: Discover new profile-matched credit cards on the web, verify them, and add them as dossiers to cards/.
argument-hint: "[how-many]  (default 3)"
allowed-tools: Task, Read, Write, WebSearch, WebFetch
---

# /scout-cards — grow the roster

Find NEW credit cards on the internet that fit the player, fact-check them, and
write them into `cards/` so `/judge-cards` can debate them later. This command
only discovers and adds — it does not run the debate.

## Resolve inputs
- COUNT  = `${1:-3}`  (how many new cards to ADD; an override, NOT a search cap —
  the scout reads as many blogs, comparison sites, and issuer pages as it needs;
  COUNT only limits how many verified survivors get written. Use a big number to
  cast wide, e.g. `/scout-cards 15`.)
- RUBRIC = `personal/requirements.md` if it exists, else `cards/requirements.md`
  (prefer the real, gitignored profile; fall back to the public example template).
- CARDS_DIR = `cards/`

## Step 1 — list what already exists (honor the roster)
List the `.md` files already in `cards/` (ignore `requirements.md`). Read
`cards/roster.json`; a card whose slug is `true` under `disabled` is benched.
Collect the `name:` lines of the ACTIVE cards so the scout doesn't duplicate a
card that's already in play. Do not research or re-add disabled cards — skip them
silently.

## Step 2 — spawn the scout
- Task → subagent `card-scout`:
  `REQUIREMENTS_PATH=<RUBRIC>. EXISTING_CARDS=<the names you listed>.
   COUNT=<COUNT>. CARDS_DIR=cards/.`

The scout reads the profile from `REQUIREMENTS_PATH`, searches the web, drops
cards that don't fit that profile or already exist, verifies each survivor with a
`card-fact-checker`, and Writes a verified dossier per survivor. After writing a
dossier, also write its fact-check verdict to `cards/.factcheck/<slug>.json`
(with `dossier_hash` + `checked_at`) so `/judge-cards` doesn't re-verify a card
the scout just checked.

## Step 3 — report
When the scout returns, print:

```
🔎 SCOUT REPORT
  Added:    <new card name>  → cards/<file>.md
            <new card name>  → cards/<file>.md
  Rejected: <card> — <reason (failed filter / unverifiable)>
  Roster now: <N> cards
```

Then remind the player they can run `/judge-cards` to battle the whole roster.

## Notes
- A game, not financial advice. Every added card is verified against its official
  issuer page before it joins the roster; unverifiable cards are rejected, not added.
- The hard filters come from the player's profile in `REQUIREMENTS_PATH` — the
  scout derives them from that file, not from any hardcoded assumption.
