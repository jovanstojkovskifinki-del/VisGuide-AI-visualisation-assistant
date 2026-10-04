"""
Enumerations shared across the whole platform.

Kept in `core` (rather than inside `datasets` or `visualizations`) because
future modules (documents, textbooks, 3D scenes) will reuse `ColumnType`-like
concepts and will definitely extend `VisualizationType`. Centralizing them
here means every app imports from one place instead of redefining choices.
"""

from django.db import models


class FileType(models.TextChoices):
    CSV = "CSV", "CSV"
    XLSX = "XLSX", "Excel (.xlsx)"


class DatasetStatus(models.TextChoices):
    UPLOADED = "UPLOADED", "Uploaded"
    PARSED = "PARSED", "Parsed"
    ANALYZED = "ANALYZED", "Analyzed"
    FAILED = "FAILED", "Failed"


class ColumnType(models.TextChoices):
    """
    Semantic type detected for a column — distinct from the raw pandas
    dtype. A column can be dtype `float64` but semantically LATITUDE, for
    example. This is what the recommendation engine's rules key off of.
    """

    NUMERIC = "NUMERIC", "Numeric"
    CATEGORICAL = "CATEGORICAL", "Categorical"
    DATETIME = "DATETIME", "Datetime"
    BOOLEAN = "BOOLEAN", "Boolean"
    LATITUDE = "LATITUDE", "Latitude"
    LONGITUDE = "LONGITUDE", "Longitude"
    IDENTIFIER = "IDENTIFIER", "Identifier"
    UNKNOWN = "UNKNOWN", "Unknown"


class VisualizationType(models.TextChoices):
    """
    Registry key type. Adding a new chart (or, later, a non-chart output
    like a 3D scene) means adding one new value here plus one new
    `VisualizationProvider` — nothing else in this enum's consumers changes,
    per the Open/Closed requirement in the architecture doc.
    """

    LINE_CHART = "LINE_CHART", "Line Chart"
    BAR_CHART = "BAR_CHART", "Bar Chart"
    SCATTER_PLOT = "SCATTER_PLOT", "Scatter Plot"
    HISTOGRAM = "HISTOGRAM", "Histogram"
    HEATMAP = "HEATMAP", "Heatmap"
    GEOGRAPHIC_MAP = "GEOGRAPHIC_MAP", "Geographic Map"
    CHOROPLETH_MAP = "CHOROPLETH_MAP", "Choropleth Map"
    TABLE = "TABLE", "Table (fallback)"
    # Reserved for the future 3D module — not built in Module 1, but
    # registering the enum value now costs nothing and documents intent.
    SCENE_3D = "SCENE_3D", "3D Scene"


class RecommendationEngineType(models.TextChoices):
    RULE_BASED = "RULE_BASED", "Rule-based"
    AI = "AI", "AI (LLM-backed)"
