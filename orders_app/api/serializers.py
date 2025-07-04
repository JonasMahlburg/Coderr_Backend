"""
Serializers for orders_app that handle order creation, detail presentation,
and status updates including nested offer and user data.
"""
from rest_framework import serializers
from orders_app.models import Order
from offers_app.models import OfferDetail
from offers_app.api.serializers import OfferDetailSerializer, OfferSerializer
from django.contrib.auth.models import User


class UserSerializerForOrder(serializers.ModelSerializer):
    """
    Lightweight user serializer used to embed basic user data in order responses.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name'] 

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving Order instances.

    Includes nested, read-only representations of the customer, offer,
    and ordered detail. Accepts an offer_detail_id for order creation,
    automatically setting the related offer and price based on the selected detail.
    """

    customer = UserSerializerForOrder(read_only=True)
    offer = OfferSerializer(read_only=True)
    ordered_detail = OfferDetailSerializer(read_only=True)
    offer_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=OfferDetail.objects.all(),
        write_only=True,
        required=True
    )


    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'offer', 'ordered_detail', 'status',
            'quantity', 'price_at_order', 'created_at', 'updated_at',
            'offer_detail_id'
        ]
        read_only_fields = ['customer', 'created_at', 'updated_at', 'price_at_order', 'offer', 'ordered_detail'] 


    def create(self, validated_data):
        """
        Creates a new Order instance with the current user as the customer.

        Extracts the related offer and price from the selected offer detail,
        sets the default status to 'in_progress', and saves the order.
        """
        customer = self.context['request'].user
        validated_data.pop('customer', None)
        offer_detail = validated_data.pop('offer_detail_id', None)
        offer = offer_detail.offer
        price_at_order = offer_detail.price

        order = Order.objects.create(
            customer=customer,
            offer=offer,
            ordered_detail=offer_detail,
            price_at_order=price_at_order,
            status='in_progress',
            **validated_data
        )
        return order

    def validate(self, data):
        """
        Validates that the ordered_detail belongs to the specified offer.

        Raises:
            ValidationError: If the ordered_detail does not match the offer.
        """
        if 'offer' in data and 'ordered_detail' in data:
            offer = data['offer']
            ordered_detail = data['ordered_detail']
            if ordered_detail.offer != offer:
                raise serializers.ValidationError(
                    {"ordered_detail": "Das ausgewählte Detail gehört nicht zum angegebenen Angebot."}
                )
        return data
    

class OrderCombinedSerializer(serializers.ModelSerializer):
    """
    Read-only serializer combining order and offer detail fields for reporting purposes.
    Includes customer and business user references.
    """
    title = serializers.CharField(source='ordered_detail.title', read_only=True)
    revisions = serializers.IntegerField(source='ordered_detail.revisions', read_only=True)
    delivery_time_in_days = serializers.IntegerField(source='ordered_detail.delivery_time_in_days', read_only=True)
    price = serializers.DecimalField(source='ordered_detail.price', max_digits=10, decimal_places=2, read_only=True)
    features = serializers.JSONField(source='ordered_detail.features', read_only=True)
    offer_type = serializers.CharField(source='ordered_detail.offer_type', read_only=True)
    customer_user = serializers.PrimaryKeyRelatedField(source='customer', read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(source='offer.user', read_only=True)


    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status', 
            'created_at', 
            'updated_at' 
        ]
     
        read_only_fields = fields
        

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating the status of an existing order.
    Restricts allowed status values and validates input.
    """
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        allowed = ['in_progress', 'completed', 'cancelled']
        if value not in allowed:
            raise serializers.ValidationError(f"Status '{value}' ist nicht erlaubt.")
        return value