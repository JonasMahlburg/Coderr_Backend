"""
Custom permission classes for the auth_app API.
"""
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS



class IsOwner(BasePermission):
    """
    Permission class that allows access to the owner of the object.
    Read-only access is allowed to authenticated users.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return obj.user == request.user