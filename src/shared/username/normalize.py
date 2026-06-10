"""Username normalization pipeline."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from src.shared.username.constants import MAX_LEN, MIN_LEN

CHARSET_RE = re.compile(r"^[a-z0-9._]+$")


@dataclass(frozen=True)
class NormalizeResult:
    ok: bool
    normalized: str | None = None
    reason: str | None = None


def normalize(raw: str | None) -> NormalizeResult:
    if raw is None:
        return NormalizeResult(ok=False, reason="invalid")

    value = raw.strip()
    if value.startswith("@"):
        value = value[1:].strip()

    if not value:
        return NormalizeResult(ok=False, reason="invalid")

    value = unicodedata.normalize("NFKC", value).lower()

    if not value.isascii():
        return NormalizeResult(ok=False, reason="invalid")

    if not CHARSET_RE.match(value):
        return NormalizeResult(ok=False, reason="invalid")

    if value.startswith(".") or value.endswith("."):
        return NormalizeResult(ok=False, reason="invalid")

    if ".." in value:
        return NormalizeResult(ok=False, reason="invalid")

    if set(value) == {"."}:
        return NormalizeResult(ok=False, reason="invalid")

    if len(value) < MIN_LEN or len(value) > MAX_LEN:
        return NormalizeResult(ok=False, reason="invalid")

    return NormalizeResult(ok=True, normalized=value)
