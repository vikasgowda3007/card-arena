---
description: One front door to the Card Arena — list, scout, or battle. Run with no argument to see the menu.
argument-hint: "[list | scout <n> | battle | list disable <slug> | list enable <slug>]"
allowed-tools: Task, Read, Write, WebSearch, WebFetch
---

# /arena — universal command

A single entry point for the whole game. The first word you type chooses the
operation; the rest are its arguments. This command dispatches to the same logic
as the standalone `/judge-cards`, `/scout-cards`, and `/list-cards` commands.

## Resolve inputs
- SUB  = `${1:-menu}`   (the operation: `menu`, `list`, `scout`, `battle`)
- REST = `${2:-}` `${3:-}`  (arguments for that operation)

## If SUB is empty or `menu` or `help` — show the menu and STOP
Print exactly this, then wait for the player to run /arena again. Do NOT launch
anything.

```
🃏 CARD ARENA — what would you like to do?

  /arena list                     show the roster (active / disabled cards)
  /arena list disable <slug>      bench a card (silently skipped in battles)
  /arena list enable  <slug>      bring a benched card back
  /arena scout [n]                discover n profile-matched cards (default 3),
                                  verify them, add to the roster
  /arena battle                   run the whole-pool tournament; crown a champion

  Examples:
    /arena scout 8
    /arena list disable discover_it_student
    /arena battle

  Tip: start small — /arena scout 3, then /arena battle.
```

## If SUB is `list` — roster manager
Follow the logic in `.claude/commands/list-cards.md` exactly, using:
- ACTION = `${2:-list}`  (`list`, `enable`, or `disable`)
- SLUG   = `${3:-}`
So `/arena list` lists; `/arena list disable <slug>` benches a card; `/arena list
enable <slug>` restores it.

## If SUB is `scout` — discover new cards
Follow the logic in `.claude/commands/scout-cards.md` exactly, with
COUNT = `${2:-3}`. It searches the web for profile-matched cards, honors the
roster (skips disabled), fact-checks each survivor, and writes verified dossiers
to `cards/`.

## If SUB is `battle` — run the tournament
Follow the logic in `.claude/commands/judge-cards.md` exactly: build the ACTIVE
field from `cards/` + `cards/roster.json` (silently skipping disabled cards),
verify each card once, run the round-robin, and crown a champion. Honor the
cost guardrail (warn + confirm above 6 active cards).

## If SUB is anything else
Tell the player it's an unknown operation and re-print the menu above.

## Notes
- The standalone commands still work; `/arena` is just the unified front door.
- A game, not financial advice.
