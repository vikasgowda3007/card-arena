"""The two contestant agents and the judge agent.

Each contestant agent is given exactly ONE card dossier and told to argue for
it. The judge is given the requirements rubric plus the full transcript and
must pick a winner. Prompts are built deterministically so they can be unit
tested without ever calling the model (see build_*_prompt).
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from .dossier import Card
from .llm import LLM


@dataclass
class Turn:
    speaker: str          # codename / "JUDGE"
    card_name: str
    round_no: int
    text: str


def build_opening_prompt(card: Card, opponent: Card) -> str:
    return (
        f"You represent this credit card and must win it the title of "
        f"the player's first card. Your card:\n\n{card.raw}\n\n"
        f"Your opponent is: {opponent.display}. "
        f"Give a punchy opening argument (max 120 words) for why YOUR card "
        f"deserves to win, grounded only in the dossier above. Stay in character "
        f"as '{card.fields.get('codename', card.name)}'."
    )


def build_rebuttal_prompt(card: Card, opponent: Card, opponent_text: str) -> str:
    return (
        f"You represent {card.display}. Your dossier:\n\n{card.raw}\n\n"
        f"Your opponent ({opponent.display}) just argued:\n\n\"{opponent_text}\"\n\n"
        f"Rebut them in max 120 words. Attack the weaknesses listed in their "
        f"category of card, defend your own, and stay in character."
    )


def build_judge_prompt(requirements: str, transcript: list[Turn]) -> str:
    convo = "\n\n".join(f"[{t.speaker}] {t.text}" for t in transcript)
    return (
        f"You are the impartial judge of a credit-card debate. Here is the "
        f"player's weighted rubric:\n\n{requirements}\n\n"
        f"Here is the full debate transcript:\n\n{convo}\n\n"
        f"Score EACH card 0-100 using the weighted criteria. Be skeptical of "
        f"claims not supported by a dossier. Then declare a winner.\n"
        f"Respond as STRICT JSON only, no prose:\n"
        f'{{"scores": {{"<card name>": <int>, "<card name>": <int>}}, '
        f'"winner": "<card name>", "reasoning": "<2-3 sentences>"}}'
    )


class ContestantAgent:
    SYSTEM = (
        "You are a sharp, persuasive debate agent representing a single credit "
        "card. You argue only from your dossier. You never invent terms. You are "
        "concise and stay in character."
    )

    def __init__(self, card: Card, llm: LLM):
        self.card = card
        self.llm = llm

    def opening(self, opponent: Card) -> str:
        return self.llm.complete(self.SYSTEM, build_opening_prompt(self.card, opponent))

    def rebuttal(self, opponent: Card, opponent_text: str) -> str:
        return self.llm.complete(
            self.SYSTEM, build_rebuttal_prompt(self.card, opponent, opponent_text)
        )


class JudgeAgent:
    SYSTEM = (
        "You are an impartial, numerate judge. You honor the weighted rubric, "
        "discount unsupported claims, and output strict JSON only."
    )

    def __init__(self, requirements: str, llm: LLM):
        self.requirements = requirements
        self.llm = llm

    def verdict(self, transcript: list[Turn]) -> dict:
        raw = self.llm.complete(
            self.SYSTEM, build_judge_prompt(self.requirements, transcript)
        )
        return _coerce_json(raw)


def _coerce_json(text: str) -> dict:
    """Models sometimes wrap JSON in fences or prose. Extract the object."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return {"error": "could not parse judge output", "raw": text}
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {"error": "invalid JSON from judge", "raw": text}
