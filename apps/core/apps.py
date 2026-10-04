from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Shared-kernel app.

    Holds only cross-cutting interfaces (ABCs), enums, exceptions, and
    framework-agnostic utilities. Deliberately contains no models and no
    business logic of its own — every other app depends on `core`, but
    `core` depends on nothing app-specific, keeping the dependency graph
    acyclic and the domain layer importable without Django being fully
    configured.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"
