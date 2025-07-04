import django_filters
from rest_framework import viewsets, mixins, filters
from offers_app.models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferListSerializer, OfferRetrieveSerializer, OfferPatchSerializer, OfferDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .permissions import IsBusinessOrReadOnly, IsOfferOwnerOrReadOnly
from .pagination import OffersResultPagination
from .filters import OfferFilter
from django.db.models import Min
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.exceptions import ValidationError

"""
API views for managing Offer and OfferDetail resources.

Includes full CRUD operations for OfferViewSet, with support for filtering,
searching, ordering, and pagination. Also includes a detail viewset for
retrieving, updating, and deleting individual OfferDetail instances.
"""

class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Offer instances.

    Provides CRUD operations and supports filtering, searching, ordering, and pagination.
    Handles user-specific permissions and annotated minimum values for price and delivery time.
    """
    queryset = Offer.objects.all()

    def get_queryset(self):
        """
        Returns a queryset of Offer objects annotated with minimum price and delivery time,
        ordered by the most recently updated.
        """
        return Offer.objects.annotate(
            overall_min_price=Min('details__price'),
            overall_min_delivery_time=Min('details__delivery_time_in_days')
        ).distinct().order_by('-updated_at')

    permission_classes = [IsBusinessOrReadOnly, IsOfferOwnerOrReadOnly]
    pagination_class = OffersResultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'overall_min_price', 'overall_min_delivery_time']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the current action.
        """
        if self.action == 'list':
            return OfferListSerializer
        elif self.action == 'retrieve':
            return OfferRetrieveSerializer
        elif self.action == 'partial_update':
            return OfferPatchSerializer
        return OfferSerializer

    def perform_create(self, serializer):
        """
        Saves a new Offer instance and assigns the current user as the owner.
        """
        serializer.save(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        """
        Handles partial update (PATCH) for an Offer instance.

        Ensures each detail contains an 'offer_type' and handles missing or invalid data gracefully.
        """
        if not request.data:
            return Response(
                {"detail": "no id"},
                status=status.HTTP_404_NOT_FOUND
                )
            
        for detail in request.data.get("details", []):
            if "offer_type" not in detail:
                return Response(
                    {"detail": "Missing 'offer_type' in one or more details."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        try:
             instance = self.get_object()
        except Http404:
           return Response(
                {"detail": "no id"},
                status=status.HTTP_404_NOT_FOUND
           )
               
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
         
    def list(self, request, *args, **kwargs):
        """
        Returns a list of offers, filtered and paginated as needed.

        Handles invalid filter parameters by returning a validation error.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
        except (django_filters.exceptions.FieldLookupError, ValueError):
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Invalid filter parameter."})

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OfferDetailViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """
    ViewSet for managing individual OfferDetail instances.

    Supports retrieve, partial update, and delete operations.
    Requires authentication.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']