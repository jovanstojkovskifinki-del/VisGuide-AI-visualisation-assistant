"""
End-to-end smoke test: upload -> parse -> analyze -> recommend -> configure,
run against the five example datasets from the spec. Not a pytest suite —
a standalone script for a quick sanity pass across the whole pipeline.

Run with:
    DJANGO_SETTINGS_MODULE=config.settings.test python tests/integration/run_e2e_smoke.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")

import django  # noqa: E402

django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile  # noqa: E402

from apps.analysis.services.analysis_service import AnalysisService  # noqa: E402
from apps.datasets.services.ingestion_service import DatasetIngestionService  # noqa: E402
from apps.recommendations.services import RecommendationService  # noqa: E402
from apps.visualizations.services import VisualizationConfigService  # noqa: E402

SAMPLE_DIR = Path(__file__).resolve().parent / "sample_data"

DATASETS = [
    ("sales_over_time.csv", "text/csv", "Sales over time -> expect LINE_CHART"),
    ("student_grades.csv", "text/csv", "Student grades -> expect BAR_CHART"),
    (
        "air_pollution.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "Air pollution (geo) -> expect GEOGRAPHIC_MAP",
    ),
    ("correlation_matrix.csv", "text/csv", "4 numeric columns -> expect HEATMAP"),
    ("age_distribution.csv", "text/csv", "Single numeric column -> expect HISTOGRAM"),
]


def run() -> None:
    ingestion = DatasetIngestionService()
    analysis = AnalysisService()
    recommendation = RecommendationService()
    config = VisualizationConfigService()

    failures = []

    for filename, content_type, expectation in DATASETS:
        print(f"\n{'=' * 70}\n{filename}  ({expectation})\n{'=' * 70}")
        file_path = SAMPLE_DIR / filename
        with open(file_path, "rb") as f:
            uploaded = SimpleUploadedFile(filename, f.read(), content_type=content_type)

        try:
            dataset = ingestion.ingest(uploaded)
            print(f"  Uploaded:        status={dataset.status}, rows={dataset.row_count}, cols={dataset.column_count}")

            profile = analysis.analyze(dataset)
            types = [cp.detected_type for cp in profile.column_profiles.all()]
            print(f"  Analyzed:        column types={types}")
            print(f"  Correlation:     {'present' if profile.correlation_matrix else 'none'}")

            result = recommendation.get_recommendation(profile)
            print(f"  Recommendation:  {result.visualization_type}  (rule={result.matched_rule}, confidence={result.confidence})")
            print(f"                   reasoning: {result.reasoning}")

            viz_config = config.generate(profile, result)
            print(f"  Config:          type={viz_config.visualization_type}, title='{viz_config.title}'")
            print(f"                   xAxis={viz_config.x_axis}")
            print(f"                   yAxis={viz_config.y_axis}")
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED: {exc!r}")
            failures.append((filename, exc))

    print(f"\n{'=' * 70}")
    if failures:
        print(f"{len(failures)} dataset(s) failed:")
        for filename, exc in failures:
            print(f"  - {filename}: {exc}")
        sys.exit(1)
    else:
        print("All datasets processed successfully end-to-end.")


if __name__ == "__main__":
    run()
