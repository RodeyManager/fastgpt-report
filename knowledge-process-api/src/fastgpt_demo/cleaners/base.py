from __future__ import annotations

from abc import ABC, abstractmethod


class CleanRule(ABC):
    name: str = ""
    description: str = ""
    default_enabled: bool = True

    @abstractmethod
    def apply(self, text: str, **kwargs) -> str:
        ...

    def should_run(self, options: dict) -> bool:
        return options.get(self.name, self.default_enabled)
