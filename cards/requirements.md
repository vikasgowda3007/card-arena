# The Prize — the player's requirements (judge's rubric)

> The judge agent reads THIS file. It scores both contestants against these
> criteria and declares which card wins the right to be the player's first card.
>
> This is an **example template**. Build your own personalised rubric by running
> `/build-profile` inside Claude Code — it interviews you and writes your real
> profile to `personal/requirements.md` (which is gitignored, never published).

## Player profile
- Describe the player here: student vs working, credit history depth, income band.
- Major spend categories (e.g. groceries, dining, bills, travel).
- Categories the player never spends on (so a card's perks there are wasted).

## Weighted criteria (weights sum to 100)
- no_annual_fee: 10
- upfront_welcome_bonus: 20
- groceries_rewards: 25
- online_shopping_rewards: 10
- bills_floor_rate: 10
- no_wasted_categories: 5
- approval_odds_no_us_history: 15
- builds_credit: 5

## Judging notes
- Pick weights that reflect what actually matters to the player; they must sum to 100.
- An upfront bonus the player can't get (because they're declined) is worth nothing — weigh approval against bonus.
- Equal-weighting all criteria is a trap; honor the weights above.
