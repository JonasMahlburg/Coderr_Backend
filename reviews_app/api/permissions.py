from rest_framework.permissions import BasePermission

class IsCustomerAndAuthenticated(BasePermission):
    """
    Allows only authenticated users with a customer profile.
    Does NOT check for duplicate reviews here.
    Only the creator of the review can edit or delete it.
    All authenticated users can read reviews.
    """

    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated

        if request.method == 'POST':
            if not request.user or not request.user.is_authenticated:
                return False
            if not hasattr(request.user, 'userprofile'):
                return False
            if request.user.userprofile.type != 'customer':
                return False
            # No duplicate review check here; validation layer handles this.
            return True

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in ['PATCH', 'DELETE']:
            return obj.reviewer == request.user
        return True