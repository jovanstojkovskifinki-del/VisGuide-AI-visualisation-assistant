"""
AssetMapper — reserved extension point for the future Interactive 3D
Visualization Module. NOT used anywhere in Module 1.

Once the 3D module exists, a concrete AssetMapper will take AI-extracted
concept names (e.g. "stomach", "liver") and map them to predefined 3D
asset references (e.g. "stomach.glb"). Defining the contract now, while
building Module 1, means the eventual `Scene3DProvider` (a
VisualizationProvider implementation) has a stable dependency to code
against without waiting for Module 1's registry/service patterns to be
retrofitted.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class AssetReference:
    concept_name: str
    asset_path: str
    asset_type: str = "glb"


class AssetMapper(ABC):
    """Maps extracted concept names to predefined 3D asset references."""

    @abstractmethod
    def map_concepts(self, concepts: list[str]) -> list[AssetReference]:
        raise NotImplementedError
