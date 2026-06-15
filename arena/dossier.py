"""Parse a card dossier (.md) into a structured Card.

A dossier is just a markdown file. We extract a few light fields for display
and pass the full raw text to the agent — the LLM reads the prose, we don't
try to over-parse it. This keeps parsing testable WITHOUT any API key.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Card:
    name: str
    codename: str
    raw: str
    path: Path
    fields: dict = field(default_factory=dict)

    @property
    def display(self) -> str:
        return f"{self.name} “{self.codename}”" if self.codename else self.name


_KV = re.compile(r"^-\s*([a-z_]+)\s*:\s*(.+)$", re.IGNORECASE)


def parse_card(path: str | Path) -> Card:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dossier not found: {path}")
    raw = path.read_text(encoding="utf-8")

    name = _first_heading(raw) or path.stem
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        m = _KV.match(line.strip())
        if m:
            key, val = m.group(1).lower(), m.group(2).strip()
            fields.setdefault(key, val)

    return Card(
        name=fields.get("name", name),
        codename=fields.get("codename", ""),
        raw=raw,
        path=path,
        fields=fields,
    )


def _first_heading(text: str) -> str | None:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return None
