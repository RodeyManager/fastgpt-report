from __future__ import annotations

from .base import CleanRule

_REGISTRY: dict[str, CleanRule] = {}


def register(rule: CleanRule) -> None:
    _REGISTRY[rule.name] = rule


def get(name: str) -> CleanRule:
    return _REGISTRY[name]


def get_all_rules() -> list[CleanRule]:
    return list(_REGISTRY.values())


def clear() -> None:
    _REGISTRY.clear()
