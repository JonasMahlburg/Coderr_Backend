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

class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Offer objects.
    Supports list, create, retrieve, update, and delete operations.
    Applies filtering, searching, and pagination for offer listings.
    """
    queryset = Offer.objects.all()

    def get_queryset(self):
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
        if self.action == 'list':
            return OfferListSerializer
        elif self.action == 'retrieve':
            return OfferRetrieveSerializer
        elif self.action == 'partial_update':
            return OfferPatchSerializer
        return OfferSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
         return super().partial_update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
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
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']