"""Small shared helpers used by multiple VisualizationProvider implementations."""

from typing import Any

from apps.analysis.models import DatasetProfile


def axis_spec(profile: DatasetProfile, column_name: str) -> dict[str, Any]:
    """Builds a standardized {column, label, type} axis descriptor."""
    column_profile = next(
        (cp for cp in profile.column_profiles.all() if cp.column_name == column_name),
        None,
    )
    return {
        "column": column_name,
        "label": column_name.replace("_", " ").title(),
        "type": column_profile.detected_type if column_profile else None,
    }


def base_metadata(profile: DatasetProfile, recommendation) -> dict[str, Any]:
    return {
        "dataset_id": str(profile.dataset_id),
        "matched_rule": recommendation.matched_rule,
        "confidence": recommendation.confidence,
        "reasoning": recommendation.reasoning,
    }
