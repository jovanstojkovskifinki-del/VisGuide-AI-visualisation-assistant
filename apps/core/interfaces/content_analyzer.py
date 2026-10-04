"""
ContentAnalyzer is the contract for "turn parsed content into a profile
describing what it means and how good it is."

Module 1 has exactly one implementation: `analysis.services.StructuredDataAnalyzer`,
which takes a `ParsedDataset` and returns a `DatasetProfile`.

Future modules implement the same shape with different types:
  - DocumentAnalyzer(ContentAnalyzer[ParsedDocument, DocumentProfile])
  - TextbookAnalyzer(ContentAnalyzer[ParsedTextbook, ConceptProfile])

Because every analyzer honors `analyze(parsed) -> profile`, a future
orchestrator can route content to the correct analyzer by content type
without special-casing each one in view/service code.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TParsedContent = TypeVar("TParsedContent")
TProfile = TypeVar("TProfile")


class ContentAnalyzer(ABC, Generic[TParsedContent, TProfile]):
    """Analyzes parsed content and produces a structured profile of it."""

    @abstractmethod
    def analyze(self, parsed_content: TParsedContent) -> TProfile:
        """
        Run analysis over already-parsed content and return a profile
        object describing its structure, quality, and semantics.

        Must not perform I/O beyond what's needed for computation (no
        network calls, no DB writes) — persistence is the caller's job.
        """
        raise NotImplementedError
