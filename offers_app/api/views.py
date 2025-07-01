# offers_app/views.py
# offers_app/views.py
from rest_framework import viewsets, mixins, filters
from offers_app.models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferListSerializer, OfferRetrieveSerializer, OfferPatchSerializer, OfferDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsBusinessOrReadOnly, IsOfferDetailOwnerOrReadOnly
from .pagination import OffersResultPagination
from .filters import OfferFilter
from django.db.models import Min # Importiere Min


class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Offer objects.
    Supports list, create, retrieve, update, and delete operations.
    Applies filtering, searching, and pagination for offer listings.
    """
    # Queryset wird in get_queryset annotiert
    def get_queryset(self):
        return Offer.objects.annotate(
            overall_min_price=Min('details__price'),
            overall_min_delivery_time=Min('details__delivery_time_in_days')
        ).order_by('-updated_at')

    permission_classes = [IsBusinessOrReadOnly]
    pagination_class = OffersResultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    # Ordering auf annotierte Felder
    ordering_fields = ['updated_at', 'overall_min_price', 'overall_min_delivery_time']

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
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsOfferDetailOwnerOrReadOnly]
    http_method_names = ['get', 'patch', 'delete']