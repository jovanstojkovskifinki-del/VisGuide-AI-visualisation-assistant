"""
Re-exports `ContentAnalyzer` from `apps.core.interfaces` so analysis-app
code can `from apps.analysis.interfaces import ContentAnalyzer` without
every file needing to know the shared kernel lives in `core`. The actual
definition (and the contract future DocumentAnalyzer/TextbookAnalyzer will
also implement) lives in apps/core/interfaces/content_analyzer.py — do not
redefine it here.
"""

from apps.core.interfaces.content_analyzer import ContentAnalyzer

__all__ = ["ContentAnalyzer"]
