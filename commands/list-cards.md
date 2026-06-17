---
description: List every card in the roster with its active/disabled status, and turn cards on or off.
argument-hint: "[enable|disable <card-slug>]   (no args = just list)"
allowed-tools: Read, Write
---

# /list-cards — roster manager

Show every card the arena knows about and whether it's active. Optionally flip a
card on or off. Disabled cards are silently skipped by `/judge-cards` and
`/scout-cards` research — they stay on disk but sit out.

## How active/disabled works
- The registry is `cards/roster.json`, shape: `{ "disabled": { "<slug>": true } }`.
- **A card is ACTIVE unless its slug is listed under `disabled` as `true`.**
  Absence = active. So the file only ever records the cards you turned OFF.
- `slug` = the dossier filename without `.md` (e.g. `boa_student`).

## Resolve inputs
- ACTION = `${1:-list}`   (one of: `list`, `enable`, `disable`)
- SLUG   = `${2:-}`

## If ACTION is `disable` or `enable`
1. Read `cards/roster.json` (create the default `{ "disabled": {} }` if missing).
2. Confirm `cards/<SLUG>.md` exists; if not, tell the player the slug is unknown
   and list valid slugs.
3. `disable` → set `disabled[SLUG] = true`. `enable` → remove `SLUG` from
   `disabled`. Write the file back.
4. Print a one-line confirmation, then fall through to the listing below.

## Always — print the roster
1. List every `cards/*.md` except `requirements.md`.
2. For each, Read its `name:` and `codename:` lines, and look up its status in
   `roster.json`.
3. Print:
```
🃏 ROSTER  (active cards fight in /judge-cards)
  ● <name> "<codename>"          [active]    <slug>
  ● <name> "<codename>"          [active]    <slug>
  ○ <name> "<codename>"          [disabled]  <slug>

  Active: <A> / <total>
```
Use ● for active, ○ for disabled.
4. If any cards are disabled, remind the player: `enable one with
   /list-cards enable <slug>`.

## Notes
- Disabling never deletes a dossier; it just benches the card.
- A game, not financial advice.
