from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from django.db import models
from django.contrib.auth.models import User

# New OfferDetailSerializer for writable nested details
class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)
    min_price = serializers.SerializerMethodField(read_only=True)
    min_delivery_time = serializers.SerializerMethodField(read_only=True)
    user_details = serializers.SerializerMethodField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]
    def validate(self, data):
        # Nur prüfen, wenn 'details' im Payload enthalten sind
        if 'details' in self.initial_data:
            details = data.get('details', None)
            if details is not None and len(details) < 3:
                raise serializers.ValidationError({"details": "Ein Angebot muss mindestens 3 Details enthalten."})
        return data

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail in details_data:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer

    def get_min_price(self, obj):
        return obj.details.aggregate(models.Min('price'))['price__min'] or 0

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(models.Min('delivery_time_in_days'))['delivery_time_in_days__min'] or 0

    def get_user_details(self, obj):
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'username': obj.user.username
        }

class OfferListSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'image', 'description', 'details'
        ]
class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(f'/api/offerdetails/{obj.id}/')


class OfferRetrieveSerializer(serializers.ModelSerializer):
    # Ändere dies von OfferDetailLinkSerializer zu OfferDetailSerializer
    details = OfferDetailSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField(read_only=True) # Füge dies hinzu, falls es im GET Response sein soll

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details' # Füge user_details hinzu
        ]

    def get_min_price(self, obj):
        return obj.details.aggregate(models.Min('price'))['price__min'] or 0

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(models.Min('delivery_time_in_days'))['delivery_time_in_days__min'] or 0

    # Füge diese Methode hinzu, da sie im OfferSerializer vorhanden ist und du sie vielleicht auch hier haben möchtest
    def get_user_details(self, obj):
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'username': obj.user.username
        }
    

class OfferPatchSerializer(serializers.ModelSerializer):

    details = OfferDetailSerializer(many=True, required=False)
    min_price = serializers.SerializerMethodField(read_only=True)
    min_delivery_time = serializers.SerializerMethodField(read_only=True)
    user_details = serializers.SerializerMethodField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault()) # user bleibt hidden

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]


    def validate(self, data):
        # Diese Validierung wird nur durchgeführt, wenn 'details' im PATCH-Payload enthalten ist.
        if 'details' in data: # Prüfen, ob 'details' im validierten Daten-Dictionary ist
            details = data.get('details')
            if details is not None and len(details) < 3:
                raise serializers.ValidationError({"details": "Ein Angebot muss mindestens 3 Details enthalten."})
        return data

    def update(self, instance, validated_data):
        # Hole die Details, falls sie im validated_data enthalten sind
        details_data = validated_data.pop('details', None)

        # Aktualisiere die Hauptfelder des Angebots
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Wenn 'details' im Payload des PATCH-Requests gesendet wurde:
        if details_data is not None:
            # Lösche alle bestehenden Details und erstelle neue aus den gesendeten Daten.
            # Dies ist die einfachste Strategie für verschachtelte PATCH-Updates,
            # bei der die gesendete Liste die bestehende vollständig ersetzt.
            instance.details.all().delete()
            for detail_data in details_data:
                OfferDetail.objects.create(offer=instance, **detail_data)
        # Beachten: Wenn 'details' NICHT im Payload ist, bleiben die bestehenden Details unverändert.
        # Wenn 'details' explizit als leere Liste gesendet wird (z.B. "details": []),
        # dann würde 'details_data' eine leere Liste sein und der Block würde die Details löschen.

        return instance

    def get_min_price(self, obj):
        return obj.details.aggregate(models.Min('price'))['price__min'] or 0

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(models.Min('delivery_time_in_days'))['delivery_time_in_days__min'] or 0

    def get_user_details(self, obj):
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'username': obj.user.username
        }