"""
Domain exception hierarchy.

Services and engines raise these instead of framework-specific exceptions.
A single DRF exception handler (see apps/core/error_handling.py) maps
`DomainError` subclasses to HTTP responses, so views never need their own
try/except blocks for domain errors.
"""


class DomainError(Exception):
    """Base class for all errors raised by the domain/service layer."""

    default_message = "A domain error occurred."
    http_status = 400

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)
        self.message = message or self.default_message


class UnsupportedFileTypeError(DomainError):
    default_message = "This file type is not supported."
    http_status = 415


class FileTooLargeError(DomainError):
    default_message = "The uploaded file exceeds the maximum allowed size."
    http_status = 413


class DatasetParsingError(DomainError):
    default_message = "The dataset could not be parsed."
    http_status = 422


class EmptyDatasetError(DatasetParsingError):
    default_message = "The dataset contains no rows or no columns."


class AnalysisError(DomainError):
    default_message = "The dataset could not be analyzed."
    http_status = 422


class NoRecommendationFoundError(DomainError):
    default_message = "No suitable visualization could be recommended for this dataset."
    http_status = 422


class UnsupportedVisualizationTypeError(DomainError):
    default_message = "No provider is registered for this visualization type."
    http_status = 422


class DatasetNotFoundError(DomainError):
    default_message = "Dataset not found."
    http_status = 404
