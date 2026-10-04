"""
Single DRF exception handler for the whole project. Wired in via
config.settings.base -> REST_FRAMEWORK["EXCEPTION_HANDLER"].

This is what keeps views free of try/except blocks for domain errors:
services and engines raise a DomainError subclass, and it is translated
here into a consistent JSON error response with the right HTTP status.
"""

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_exception_handler

from apps.core.exceptions import DomainError


def domain_aware_exception_handler(exc, context):
    if isinstance(exc, DomainError):
        return Response(
            {"error": exc.__class__.__name__, "detail": exc.message},
            status=exc.http_status,
        )
    return drf_default_exception_handler(exc, context)
