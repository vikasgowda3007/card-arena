"""Command-line entry point: `python -m arena` or `card-arena`."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .agents import build_opening_prompt
from .arena import Arena
from .dossier import parse_card
from .llm import LLM, NoBackendAvailable

CARDS_DIR = Path(__file__).resolve().parent.parent / "cards"

BOLD, DIM, CYAN, YEL, GRN, RST = (
    "\033[1m", "\033[2m", "\033[36m", "\033[33m", "\033[32m", "\033[0m",
)


def _default(name: str) -> Path:
    return CARDS_DIR / name


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="card-arena",
        description="Two AI agents debate; a judge picks the winning credit card.",
    )
    p.add_argument("--card-a", default=str(_default("boa_student.md")),
                   help="dossier for contestant A")
    p.add_argument("--card-b", default=str(_default("discover_it_student.md")),
                   help="dossier for contestant B")
    p.add_argument("--requirements", default=str(_default("requirements.md")),
                   help="judge's rubric file")
    p.add_argument("--rounds", type=int, default=2, help="rebuttal rounds (default 2)")
    p.add_argument("--model", default="claude-sonnet-4-6")
    p.add_argument("--backend", choices=["auto", "cli", "api"], default="auto",
                   help="model backend (default auto: claude CLI, else API key)")
    p.add_argument("--dry-run", action="store_true",
                   help="show matchup + sample prompt without calling the model")
    args = p.parse_args(argv)

    try:
        card_a = parse_card(args.card_a)
        card_b = parse_card(args.card_b)
        requirements = Path(args.requirements).read_text(encoding="utf-8")
    except FileNotFoundError as e:
        print(f"{YEL}{e}{RST}", file=sys.stderr)
        return 2

    print(f"\n{BOLD}🃏  CARD ARENA{RST}")
    print(f"{DIM}The prize: the player's first credit card.{RST}\n")
    print(f"  {CYAN}A:{RST} {card_a.display}")
    print(f"  {CYAN}B:{RST} {card_b.display}")
    print(f"  {DIM}Rounds: {args.rounds}  ·  Backend: {args.backend}{RST}\n")

    if args.dry_run:
        print(f"{YEL}— dry run —{RST} no model called.\n")
        print(f"{BOLD}Sample opening prompt for A:{RST}\n")
        print(DIM + build_opening_prompt(card_a, card_b) + RST)
        return 0

    llm = LLM(model=args.model, backend=args.backend)

    def on_turn(turn):
        tag = "JUDGE" if turn.speaker == "JUDGE" else turn.speaker
        head = f"{BOLD}{tag}{RST} {DIM}(round {turn.round_no}){RST}"
        print(f"{head}\n{turn.text}\n")

    try:
        result = Arena(card_a, card_b, requirements,
                       rounds=args.rounds, llm=llm).run(on_turn=on_turn)
    except NoBackendAvailable as e:
        print(f"{YEL}{e}{RST}", file=sys.stderr)
        return 3
    except RuntimeError as e:
        print(f"{YEL}Model backend error: {e}{RST}", file=sys.stderr)
        return 3

    v = result.verdict
    print(f"{BOLD}⚖️  VERDICT{RST}")
    if "error" in v:
        print(f"{YEL}Judge output could not be parsed:{RST}\n{v.get('raw', '')}")
        return 4
    for name, score in v.get("scores", {}).items():
        print(f"  {name}: {BOLD}{score}{RST}")
    print(f"\n  {GRN}{BOLD}WINNER: {v.get('winner', '?')}{RST}")
    print(f"  {DIM}{v.get('reasoning', '')}{RST}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
