"""Reserved usernames and blocked patterns."""

from __future__ import annotations

BLOCKED_EXACT: frozenset[str] = frozenset(
    {
        "admin",
        "administrator",
        "api",
        "help",
        "login",
        "logout",
        "moderator",
        "null",
        "official",
        "root",
        "signup",
        "studio3",
        "support",
        "system",
        "undefined",
        "www",
    }
)

BLOCKED_PREFIXES: tuple[str, ...] = ("admin", "studio3", "support")


def is_blocked(normalized: str) -> bool:
    if normalized in BLOCKED_EXACT:
        return True
    return any(normalized.startswith(p) for p in BLOCKED_PREFIXES)
