from rest_framework.permissions import BasePermission


class AllowAnyForMVP(BasePermission):
    """
    Explicit placeholder permission for Module 1.

    Module 1 has no auth/ownership requirements yet (datasets aren't
    scoped to users). Naming this explicitly — rather than leaving views
    unauthenticated by omission — makes it a deliberate, greppable
    decision to tighten later (e.g. IsOwnerOrReadOnly once user accounts
    are introduced).
    """

    def has_permission(self, request, view) -> bool:
        return True
