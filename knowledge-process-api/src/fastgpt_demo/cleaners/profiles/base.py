from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CleanProfile:
    name: str
    description: str
    rules: dict[str, bool] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)

    def to_options_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result.update(self.rules)
        result.update(self.params)
        return result
