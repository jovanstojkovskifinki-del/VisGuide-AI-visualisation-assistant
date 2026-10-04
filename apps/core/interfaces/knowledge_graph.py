"""
KnowledgeGraph — reserved extension point for a future concept-graph /
textbook module. NOT used anywhere in Module 1.
"""

from abc import ABC, abstractmethod
from typing import Any


class KnowledgeGraph(ABC):
    """Accumulates concept nodes and relationships, exportable as JSON."""

    @abstractmethod
    def add_concept(self, concept_name: str, metadata: dict[str, Any] | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_relationship(self, source: str, target: str, relationship_type: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> dict[str, Any]:
        raise NotImplementedError
