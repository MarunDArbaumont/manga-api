from rest_framework import permissions
from rest_framework.throttling import AnonRateThrottle

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_id == request.user.id

class SignupThrottle(AnonRateThrottle):
    rate = "10/hour"