from rest_framework.permissions import BasePermission, IsAuthenticated

__all__ = ["IsAuthenticated", "ReadOnly"]


class ReadOnly(BasePermission):
    """Allows only safe methods (GET/HEAD/OPTIONS)."""

    def has_permission(self, request, view) -> bool:
        return request.method in ("GET", "HEAD", "OPTIONS")
