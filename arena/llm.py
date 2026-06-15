"""Backends for live model calls.

Two backends, auto-detected in this order:
  1. CLI backend  — shells out to the `claude` command (works when you run this
     project inside Claude CLI; no API key needed).
  2. API backend  — uses the `anthropic` SDK with ANTHROPIC_API_KEY.

If neither is available we fail loudly with a helpful message rather than
silently faking output. `--dry-run` bypasses this entirely.
"""
from __future__ import annotations

import os
import shutil
import subprocess


class NoBackendAvailable(RuntimeError):
    pass


class LLM:
    def __init__(self, model: str = "claude-sonnet-4-6", max_tokens: int = 700,
                 backend: str = "auto"):
        self.model = model
        self.max_tokens = max_tokens
        self.backend = backend
        self._api_client = None
        self._resolved = None

    def _resolve(self) -> str:
        if self._resolved:
            return self._resolved
        if self.backend in ("cli", "auto") and shutil.which("claude"):
            self._resolved = "cli"
        elif self.backend in ("api", "auto") and os.environ.get("ANTHROPIC_API_KEY"):
            self._resolved = "api"
        else:
            raise NoBackendAvailable(
                "No model backend available.\n"
                "This arena makes live Claude calls. Either:\n"
                "  • run it inside Claude CLI (the `claude` command on PATH), or\n"
                "  • set an API key:  export ANTHROPIC_API_KEY=sk-ant-...\n"
                "Use --dry-run to preview the matchup and prompts without a model."
            )
        return self._resolved

    def complete(self, system: str, user: str) -> str:
        backend = self._resolve()
        if backend == "cli":
            return self._complete_cli(system, user)
        return self._complete_api(system, user)

    def _complete_cli(self, system: str, user: str) -> str:
        cmd = ["claude", "-p", user, "--append-system-prompt", system]
        if self.model:
            cmd += ["--model", self.model]
        proc = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=180,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"claude CLI failed: {proc.stderr.strip()}")
        return proc.stdout.strip()

    def _complete_api(self, system: str, user: str) -> str:
        if self._api_client is None:
            try:
                import anthropic
            except ImportError as e:
                raise RuntimeError(
                    "The 'anthropic' package is not installed. Run: pip install anthropic"
                ) from e
            self._api_client = anthropic.Anthropic(
                api_key=os.environ["ANTHROPIC_API_KEY"]
            )
        msg = self._api_client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(
            b.text for b in msg.content if getattr(b, "type", "") == "text"
        ).strip()
