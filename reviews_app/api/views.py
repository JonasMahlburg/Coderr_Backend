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
from .permissions import IsCustomerAndAuthenticated


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Review instances.

    Provides CRUD operations for reviews with permission enforcement:
    - Only authenticated customers can create reviews.
    - Each customer can create only one review per business user.
    - Only the creator of a review can update or delete it.
    - All authenticated users can read reviews.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsCustomerAndAuthenticated]

    def perform_create(self, serializer):
        """
        Saves a new review instance with the current user set as the reviewer.

        Catches model validation errors and raises them as DRF validation errors.
        """
        try:
            serializer.save(reviewer=self.request.user)
        except ValidationError as e:
            raise DRFValidationError(e.message_dict)

    def list(self, request, *args, **kwargs):
        """
        Retrieves and returns a list of all reviews serialized.

        Does not apply any additional filtering or pagination.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)