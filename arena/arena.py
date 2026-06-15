"""Orchestrates a match: opening statements, N rebuttal rounds, then a verdict."""
from __future__ import annotations

from dataclasses import dataclass, field

from .agents import ContestantAgent, JudgeAgent, Turn
from .dossier import Card
from .llm import LLM


@dataclass
class MatchResult:
    transcript: list[Turn] = field(default_factory=list)
    verdict: dict = field(default_factory=dict)


class Arena:
    def __init__(self, card_a: Card, card_b: Card, requirements: str,
                 rounds: int = 2, llm: LLM | None = None):
        self.card_a = card_a
        self.card_b = card_b
        self.requirements = requirements
        self.rounds = rounds
        self.llm = llm or LLM()

    def run(self, on_turn=None) -> MatchResult:
        a = ContestantAgent(self.card_a, self.llm)
        b = ContestantAgent(self.card_b, self.llm)
        judge = JudgeAgent(self.requirements, self.llm)
        transcript: list[Turn] = []

        def record(speaker, card_name, rnd, text):
            turn = Turn(speaker, card_name, rnd, text)
            transcript.append(turn)
            if on_turn:
                on_turn(turn)

        # Round 0 — opening statements
        record(self.card_a.codename or self.card_a.name, self.card_a.name, 0,
               a.opening(self.card_b))
        record(self.card_b.codename or self.card_b.name, self.card_b.name, 0,
               b.opening(self.card_a))

        # Rebuttal rounds — both answer the other's PREVIOUS-round turn. Capture
        # both targets before generating either reply, so neither side gets to
        # rebut an argument the other only just made this round (fair, symmetric,
        # and matches the parallel-wave design of the native /judge-cards flow).
        for r in range(1, self.rounds + 1):
            last_b = _last_for(transcript, self.card_b.name)
            last_a = _last_for(transcript, self.card_a.name)
            reply_a = a.rebuttal(self.card_b, last_b)
            reply_b = b.rebuttal(self.card_a, last_a)
            record(self.card_a.codename or self.card_a.name, self.card_a.name, r,
                   reply_a)
            record(self.card_b.codename or self.card_b.name, self.card_b.name, r,
                   reply_b)

        verdict = judge.verdict(transcript)
        return MatchResult(transcript=transcript, verdict=verdict)


def _last_for(transcript: list[Turn], card_name: str) -> str:
    for turn in reversed(transcript):
        if turn.card_name == card_name:
            return turn.text
    return ""
