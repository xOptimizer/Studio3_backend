"""Profanity and blocklist validation."""

from __future__ import annotations

from src.shared.username.blocklist import is_blocked

# Minimal profanity filter for V1 — extend via config file later.
PROFANITY: frozenset[str] = frozenset({"badword"})


def is_profane(normalized: str) -> bool:
    if normalized in PROFANITY:
        return True
    for token in normalized.replace(".", "_").split("_"):
        if token and token in PROFANITY:
            return True
    return False


def validate_blocked(normalized: str) -> str | None:
    if is_blocked(normalized):
        return "blocked"
    if is_profane(normalized):
        return "blocked"
    return None
