"""
ViewSet for managing reviews in the reviews_app.
Handles CRUD operations with permission control to restrict
creation to customers who haven't reviewed a business yet,
and allows only creators to edit or delete their reviews.
"""
from rest_framework import viewsets
from rest_framework.response import Response
from reviews_app.models import Review
from reviews_app.api.serializers import ReviewSerializer
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from .permissions import IsCustomerAndNotReviewedBefore



class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Review model.
    Supports listing, creating, retrieving, updating, and deleting reviews.
    Uses custom permission to enforce business rules.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsCustomerAndNotReviewedBefore]

    def perform_create(self, serializer):
        try:
            serializer.save(reviewer=self.request.user)
        except ValidationError as e:
            raise DRFValidationError(e.message_dict)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    