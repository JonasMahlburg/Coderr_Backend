"""
ViewSets for managing offers and offer details within the offers_app.
Includes filtering, searching, ordering, and permission handling.
"""
from rest_framework import viewsets, mixins, filters
from offers_app.models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferListSerializer, OfferRetrieveSerializer, OfferDetailSerializer, OfferPatchSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsBusinessOrReadOnly, IsOfferDetailOwnerOrReadOnly
from .pagination import OffersResultPagination
from .filters import OfferFilter


class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Offer objects.
    Supports list, create, retrieve, update, and delete operations.
    Applies filtering, searching, and pagination for offer listings.
    """
    queryset = Offer.objects.all().order_by('-updated_at')
    permission_classes = [IsBusinessOrReadOnly]
    pagination_class = OffersResultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'details__delivery_time_in_days']

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


class OfferDetailViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """
    ViewSet for retrieving, updating and deleting individual OfferDetail objects.
    Only owners may update or delete; authenticated users may retrieve.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsOfferDetailOwnerOrReadOnly]
    http_method_names = ['get', 'patch', 'delete']