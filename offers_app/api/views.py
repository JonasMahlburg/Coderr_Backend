from rest_framework import generics, filters
from offers_app.models import Offer, OfferDetail
# Importiere deine neuen Serializer
from .serializers import OfferSerializer, OfferListSerializer, OfferRetrieveSerializer, OfferDetailSerializer, OfferPatchSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .permissions import IsBusinessUser, IsAuthenticated, IsOfferOwner

class OfferPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

class OfferListCreateView(generics.ListCreateAPIView):
    queryset = Offer.objects.all().order_by('-updated_at')
    permission_classes = [IsBusinessUser]
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['details__delivery_time_in_days']
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'details__delivery_time_in_days']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OfferListSerializer
        # Für POST verwenden wir weiterhin den vollständigen OfferSerializer
        return OfferSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated, IsOfferOwner]

    def get_serializer_class(self):
        if self.request.method == "GET":
    
            return OfferRetrieveSerializer
        elif self.request.method == "PATCH":
    
            return OfferPatchSerializer
      
        return OfferSerializer


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = []  # Keine Auth nötig