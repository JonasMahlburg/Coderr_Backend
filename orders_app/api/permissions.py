"""
Custom permission classes for the orders_app to control access to order-related operations.
"""
from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    """
    Permission class that grants access only to authenticated users
    whose profile type is 'customer'.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'userprofile') and
            request.user.userprofile.type == 'customer'
        )