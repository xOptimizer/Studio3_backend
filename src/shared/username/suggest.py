"""Username suggestion generator when taken."""

from __future__ import annotations


def generate_candidates(base: str) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = {base}

    def add(s: str) -> None:
        s = s[:30]
        if s and s not in seen:
            seen.add(s)
            candidates.append(s)

    if len(base) > 3:
        mid = len(base) // 2
        add(f"{base[:mid]}_{base[mid:]}")
        add(f"{base[:mid]}.{base[mid:]}")

    for suffix in ("_art", "_studio", "art", "studio"):
        add(f"{base}{suffix}")

    for n in range(1, 1000):
        add(f"{base}{n}")
        add(f"{base}_{n}")
        if len(candidates) >= 12:
            break

    return candidates[:12]
