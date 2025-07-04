"""
Permissions for the reviews_app handling review permissions.
"""
from rest_framework.permissions import BasePermission

class IsCustomerAndAuthenticated(BasePermission):
    """
    Custom permission for review-related views.

    Allows full access (read, write, edit, delete) only to authenticated users
    with a customer profile. Only the creator of a review can edit or delete it.
    All authenticated users can read reviews. Duplicate review checks are not performed here.
    """

    def has_permission(self, request, view):
        """
        Determines if the request should be permitted at the view level.

        Allows read-only methods for all authenticated users.
        Allows POST only for authenticated users with a customer profile.
        """
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated

        if request.method == 'POST':
            if not request.user or not request.user.is_authenticated:
                return False
            if not hasattr(request.user, 'userprofile'):
                return False
            if request.user.userprofile.type != 'customer':
                return False
       
            return True

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Determines if the request should be permitted at the object level.

        Allows editing and deletion only by the review's creator.
        All authenticated users may view reviews.
        """
        if request.method in ['PATCH', 'DELETE']:
            return obj.reviewer == request.user
        return True