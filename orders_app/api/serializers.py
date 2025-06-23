from rest_framework import serializers
from orders_app.models import Order # Importiere das Order-Modell
from offers_app.models import Offer, OfferDetail # Importiere die relevanten Offers-Modelle
from offers_app.api.serializers import OfferDetailSerializer, OfferSerializer # Importiere deine bestehenden Serializer
from django.contrib.auth.models import User

# Optional: Ein einfacher Serializer für den User, falls du detaillierte User-Infos brauchst
class UserSerializerForOrder(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name'] # Wähle die Felder, die du anzeigen möchtest

class OrderSerializer(serializers.ModelSerializer):
    # Felder für die lesbare Darstellung (GET-Requests)

    # Zeige detaillierte Informationen über den Kunden
    # `read_only=True` da der Kunde über den Token des eingeloggten Users gesetzt wird
    customer = UserSerializerForOrder(read_only=True)

    # Zeige detaillierte Informationen über das bestellte Offer
    # `read_only=True` für GET-Requests. Beim Erstellen wird nur die Offer-ID erwartet.
    # Du könntest auch einen einfacheren Offer-Serializer hier verwenden, der nur id und title hat.
    # Für den Moment nehmen wir den vollen OfferSerializer, aber mit read_only=True.
    offer = OfferSerializer(read_only=True)

    # Zeige detaillierte Informationen über das bestellte OfferDetail
    # `read_only=True` für GET-Requests. Beim Erstellen wird nur die OfferDetail-ID erwartet.
    ordered_detail = OfferDetailSerializer(read_only=True)

    offer_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=OfferDetail.objects.all(),
        write_only=True,
        required=True
    )

    # Zusätzliche berechnete Felder (optional, falls du sie nicht im Model hast)
    # Wenn price_at_order im Model ist, brauchst du dieses get_total_price nicht mehr als SerializerMethodField.
    # get_total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'offer', 'ordered_detail', 'status',
            'quantity', 'price_at_order', 'created_at', 'updated_at',
            'offer_detail_id'
        ]
        read_only_fields = ['customer', 'created_at', 'updated_at', 'price_at_order', 'offer', 'ordered_detail'] # Diese Felder sollten nicht vom Client gesetzt werden

    # Custom create-Methode für verschachteltes Schreiben
    # Beim Erstellen einer Bestellung (POST) sendest du nur die IDs
    # Für PATCH/PUT musst du überlegen, ob du diese Felder direkt ändern lassen willst
    def create(self, validated_data):
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
            status='in_progress',  # 👈 Hier explizit setzen
            **validated_data
        )
        return order

    # def get_total_price(self, obj):
    #     return obj.get_total_price() # Ruft die Methode aus dem Order-Modell auf

    # Validierung, falls nötig (z.B. um sicherzustellen, dass ordered_detail auch wirklich zum offer gehört)
    def validate(self, data):
        if 'offer' in data and 'ordered_detail' in data:
            offer = data['offer']
            ordered_detail = data['ordered_detail']
            if ordered_detail.offer != offer:
                raise serializers.ValidationError(
                    {"ordered_detail": "Das ausgewählte Detail gehört nicht zum angegebenen Angebot."}
                )
        return data
    

class OrderCombinedSerializer(serializers.ModelSerializer):
    # Felder aus dem OfferDetail-Modell, die direkt auf die Order-Ebene gehoben werden
    title = serializers.CharField(source='ordered_detail.title', read_only=True)
    revisions = serializers.IntegerField(source='ordered_detail.revisions', read_only=True)
    delivery_time_in_days = serializers.IntegerField(source='ordered_detail.delivery_time_in_days', read_only=True)
    price = serializers.DecimalField(source='ordered_detail.price', max_digits=10, decimal_places=2, read_only=True)
    features = serializers.JSONField(source='ordered_detail.features', read_only=True)
    offer_type = serializers.CharField(source='ordered_detail.offer_type', read_only=True)

    # Felder, die den Benutzer (Kunden) und den Business-Benutzer (Anbieter) referenzieren
    # customer_user: ID des Benutzers, der die Bestellung aufgegeben hat
    customer_user = serializers.PrimaryKeyRelatedField(source='customer', read_only=True)

    # business_user: ID des Benutzers, dem das bestellte Angebot gehört
    # Wir müssen durch das 'offer'-Feld der Order zum 'user'-Feld des Offers navigieren
    business_user = serializers.PrimaryKeyRelatedField(source='offer.user', read_only=True)


    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title', # Von OfferDetail
            'revisions', # Von OfferDetail
            'delivery_time_in_days', # Von OfferDetail
            'price', # Von OfferDetail
            'features', # Von OfferDetail
            'offer_type', # Von OfferDetail
            'status', # Vom Order-Modell
            'created_at', # Vom Order-Modell
            'updated_at' # Vom Order-Modell
        ]
        # Alle Felder in diesem Serializer sollen nur gelesen werden können für diese kombinierte Ansicht
        read_only_fields = fields

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        allowed = ['in_progress', 'completed', 'cancelled']
        if value not in allowed:
            raise serializers.ValidationError(f"Status '{value}' ist nicht erlaubt.")
        return value