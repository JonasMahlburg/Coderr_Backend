"""
Views and API endpoints for managing orders, including listing,
creating, updating orders and retrieving order counts.
"""

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from orders_app.models import Order
from .serializers import OrderCombinedSerializer, OrderStatusUpdateSerializer, OrderSerializer
from .permissions import IsCustomerUser
from django.contrib.auth.models import User


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.
    Supports list, create, retrieve, and partial update (status).
    Includes permission handling to restrict creation to customers
    and status updates to business offer owners.
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_permissions(self):
        if self.action == 'create':
            return [IsCustomerUser()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Order.objects.filter(customer=user).distinct() | \
                   Order.objects.filter(offer__user=user).distinct()
        return Order.objects.none()

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return OrderCombinedSerializer
        return self.serializer_class_map.get(self.action, OrderSerializer)

    serializer_class_map = {
        'create': OrderSerializer,
        'partial_update': OrderStatusUpdateSerializer,
    }

    def perform_create(self, serializer):
        order = serializer.save()
        order.customer = self.request.user
        order.save()
        self._created_order = order

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        combined_data = OrderCombinedSerializer(self._created_order).data
        return Response(combined_data, status=201)

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        if order.offer.user != request.user:
            return Response({'detail': 'Nur der Anbieter kann den Status aktualisieren.'}, status=403)
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        combined_serializer = OrderCombinedSerializer(order)
        return Response(combined_serializer.data, status=200)


class OrderCountView(APIView):
    """
    APIView to retrieve count of orders in progress for a given business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        user = get_object_or_404(User, pk=business_user_id)
        count = Order.objects.filter(offer__user=user, status='in_progress').count()
        return Response({'order_count': count}, status=200)


class CompletedOrderCountView(APIView):
    """
    APIView to retrieve count of completed orders for a given business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        user = get_object_or_404(User, pk=business_user_id)
        count = Order.objects.filter(offer__user=user, status='completed').count()
        return Response({'completed_order_count': count}, status=200)