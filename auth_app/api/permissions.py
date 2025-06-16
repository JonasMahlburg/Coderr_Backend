from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS



class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return obj.user == request.user