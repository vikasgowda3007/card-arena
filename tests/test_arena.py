"""Tests that run WITHOUT any model backend, using a fake LLM.

Covers: dossier parsing, prompt construction, judge JSON coercion, and a full
match flow with a scripted fake model.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import subprocess

from arena.agents import (
    build_judge_prompt,
    build_opening_prompt,
    _coerce_json,
)
from arena.arena import Arena
from arena.dossier import parse_card
from arena.llm import LLM

CARDS = Path(__file__).resolve().parent.parent / "cards"


class FakeLLM:
    """Returns scripted text; records prompts. No network, no key."""
    def __init__(self):
        self.calls = []

    def complete(self, system, user):
        self.calls.append((system, user))
        if "STRICT JSON" in user or "strict JSON" in user:
            return (
                '{"scores": {"BofA Customized Cash Rewards for Students": 78, '
                '"Discover it Student Cash Back": 71}, '
                '"winner": "BofA Customized Cash Rewards for Students", '
                '"reasoning": "Edges it on bonus and category fit."}'
            )
        return "I am the best card. Pick me."


def test_parse_card_extracts_name_and_codename():
    card = parse_card(CARDS / "boa_student.md")
    assert "Customized Cash" in card.name
    assert card.codename == "The Strategist"
    assert "annual_fee" in card.fields


def test_parse_card_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        parse_card(CARDS / "does_not_exist.md")


def test_opening_prompt_includes_dossier_and_opponent():
    a = parse_card(CARDS / "boa_student.md")
    b = parse_card(CARDS / "discover_it_student.md")
    prompt = build_opening_prompt(a, b)
    assert a.raw[:30] in prompt
    assert b.display in prompt


def test_coerce_json_handles_fenced_output():
    out = _coerce_json('```json\n{"winner": "X", "scores": {}}\n```')
    assert out["winner"] == "X"


def test_coerce_json_handles_garbage():
    assert "error" in _coerce_json("the winner is clearly X")


def test_full_match_runs_with_fake_llm():
    a = parse_card(CARDS / "boa_student.md")
    b = parse_card(CARDS / "discover_it_student.md")
    req = (CARDS / "requirements.md").read_text()
    result = Arena(a, b, req, rounds=1, llm=FakeLLM()).run()
    # opening (2) + 1 rebuttal round (2) = 4 turns
    assert len(result.transcript) == 4
    assert result.verdict["winner"].startswith("BofA")
    assert set(result.verdict["scores"]) == {
        "BofA Customized Cash Rewards for Students",
        "Discover it Student Cash Back",
    }


def test_cli_timeout_becomes_runtimeerror(monkeypatch):
    # A slow `claude` call must surface as RuntimeError (which cli.py handles),
    # not a raw subprocess.TimeoutExpired traceback.
    llm = LLM(backend="cli")
    llm._resolved = "cli"  # skip PATH detection

    def boom(*a, **k):
        raise subprocess.TimeoutExpired(cmd="claude", timeout=180)

    monkeypatch.setattr(subprocess, "run", boom)
    with pytest.raises(RuntimeError):
        llm.complete("sys", "user")


def test_judge_prompt_contains_rubric_and_transcript():
    req = (CARDS / "requirements.md").read_text()
    from arena.agents import Turn
    t = [Turn("The Strategist", "BofA", 0, "vote for me")]
    prompt = build_judge_prompt(req, t)
    assert "weighted" in prompt.lower()
    assert "vote for me" in prompt
