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
    Permission that allows read and write access only to authenticated users.
    Write access is restricted to users with profile type 'business'.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False  # Lesen nur für authentifizierte Nutzer
        
        if request.method in SAFE_METHODS:
            # Alle authentifizierten Nutzer dürfen lesen
            return True
        
        # Schreiben nur für business-User
        return (
            hasattr(request.user, 'userprofile') and
            request.user.userprofile.type == 'business'
        )


class IsOfferDetailOwnerOrReadOnly(BasePermission):
    """
    Permission class that allows read-only access to authenticated users,
    but restricts write access to the owner of the related offer.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return obj.offer.user == request.user