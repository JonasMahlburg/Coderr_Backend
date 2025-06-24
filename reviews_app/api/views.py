from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from reviews_app.models import Review
from reviews_app.api.serializers import ReviewSerializer
from django.core.exceptions import ValidationError

class IsCustomerAndAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.is_customer
        )

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsCustomerAndAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        try:
            serializer.save(reviewer=self.request.user)
        except ValidationError as e:
            from rest_framework import serializers
            raise serializers.ValidationError(e.message_dict)