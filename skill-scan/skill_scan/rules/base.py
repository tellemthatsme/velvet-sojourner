from __future__ import annotations

import os
import importlib
import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from skill_scan.models import Finding, Severity


class Rule(ABC):
    """Abstract base class for all scan rules."""

    name: str = ""
    description: str = ""
    severity: Severity = Severity.INFO

    @abstractmethod
    def match(self, file_path: Path, content: str) -> list[Finding]:
        """Check a file's content for violations.

        Returns a list of Findings (possibly empty).
        """
        ...


class RuleRegistry:
    """Singleton registry that discovers and holds all Rule instances."""

    _instance: Optional[RuleRegistry] = None

    def __new__(cls) -> RuleRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._rules: list[Rule] = []
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    def register(self, rule: Rule) -> None:
        if not isinstance(rule, Rule):
            raise TypeError(f"Expected Rule instance, got {type(rule)}")
        self._rules.append(rule)

    def register_from_module(self, module) -> None:
        for _, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, Rule)
                and obj is not Rule
            ):
                self.register(obj())

    def discover(self, directory: Optional[Path] = None) -> None:
        if directory is not None and directory.is_dir():
            for path in directory.iterdir():
                if path.suffix == ".py" and not path.name.startswith("_"):
                    spec = importlib.util.spec_from_file_location(
                        path.stem, str(path)
                    )
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        self.register_from_module(mod)

    @property
    def rules(self) -> list[Rule]:
        return list(self._rules)

    def __len__(self) -> int:
        return len(self._rules)
