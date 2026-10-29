from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow anyone to read, but only staff users to modify the catalog."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
