from rest_framework.response import Response
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
from rest_framework.exceptions import ValidationError, NotAuthenticated, PermissionDenied
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status



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


        try:
            instance = self.get_object()
        except Http404:
            return Response(
                {"detail": "There is no Offer at this given ID"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not request.user.is_authenticated:
            return Response(
                {"detail": "You must be authenticated"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if instance.user != request.user:
            return Response(
                {"detail": "You have to be the Owner"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except ValidationError as e:
            return Response(
                {"detail": "Details are not valid", "errors": e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {"detail": "Internal Servererror."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"detail": "Sucess", "data": serializer.data},
            status=status.HTTP_200_OK
        )

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