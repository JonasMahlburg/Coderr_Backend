"""
Custom permission classes for offers_app to control access to offer-related views.
"""
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class IsBusinessUser(BasePermission):
    """
    Permission class that grants access only to authenticated users
    whose profile type is 'business'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'userprofile') and
            request.user.userprofile.type == 'business'
        )


class IsOfferOwner(BasePermission):
    """
    Object-level permission to allow only the owner of the offer to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsBusinessOrReadOnly(BasePermission):
    """
    Permission that allows unrestricted read access.
    Write access is restricted to authenticated users with profile type 'business'.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            if hasattr(view, 'action') and view.action == 'retrieve':
                return request.user and request.user.is_authenticated
            return True

        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'userprofile') and
            request.user.userprofile.type == 'business'
        )


class IsOfferOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to allow only the owner of the offer to edit or delete it.
    Read permissions are allowed to any request.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
