"""
SceneDescription — reserved extension point for the future Interactive 3D
Visualization Module. NOT used anywhere in Module 1.

This defines the JSON contract a future `Scene3DProvider` would produce
and the frontend Three.js engine would consume: a list of scene objects
(mapped assets + positions), relationships between them, and educational
metadata. It intentionally mirrors the shape of `VisualizationConfig`
(title, metadata, options) so both can flow through the same
`VisualizationProvider.build_config()` seam.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SceneObject:
    concept_name: str
    asset_path: str
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    label: str | None = None
    highlight_on_click: bool = True


@dataclass(frozen=True)
class SceneDescription:
    title: str
    objects: list[SceneObject] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "objects": [obj.__dict__ for obj in self.objects],
            "relationships": self.relationships,
            "metadata": self.metadata,
        }


class SceneDescriptionBuilder(ABC):
    """Builds a SceneDescription from extracted concepts and relationships."""

    @abstractmethod
    def build(self, concepts: list[str], relationships: list[dict[str, Any]]) -> SceneDescription:
        raise NotImplementedError
