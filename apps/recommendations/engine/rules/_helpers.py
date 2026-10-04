"""Small shared helpers used by multiple Rule implementations."""

from apps.analysis.models import ColumnProfile, DatasetProfile
from apps.core.enums import ColumnType


def columns_of_type(profile: DatasetProfile, column_type: ColumnType) -> list[ColumnProfile]:
    return [cp for cp in profile.column_profiles.all() if cp.detected_type == column_type]
