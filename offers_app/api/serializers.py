# offers_app/serializers.py
from rest_framework import serializers
from offers_app.models import Offer, OfferDetail

class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, source='overall_min_price', read_only=True)
    min_delivery_time = serializers.IntegerField(source='overall_min_delivery_time', read_only=True)
    user_details = serializers.SerializerMethodField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]
    def validate(self, data):
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

    def get_user_details(self, obj):
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'username': obj.user.username
        }


class OfferListSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, source='overall_min_price', read_only=True)
    min_delivery_time = serializers.IntegerField(source='overall_min_delivery_time', read_only=True)
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_details(self, obj):
        details = obj.details.all()
        return [
            {
                'id': d.id,
                'url': f"/offerdetails/{d.id}/"
            } for d in details
        ]

    def get_user_details(self, obj):
        user = obj.user
        return {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username
        }

class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(f'/api/offerdetails/{obj.id}/')


class OfferRetrieveSerializer(serializers.ModelSerializer):
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, source='overall_min_price', read_only=True)
    min_delivery_time = serializers.IntegerField(source='overall_min_delivery_time', read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time'
        ]


class OfferPatchSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, source='overall_min_price', read_only=True)
    min_delivery_time = serializers.IntegerField(source='overall_min_delivery_time', read_only=True)
    user_details = serializers.SerializerMethodField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details', 'offer_type'
        ]

    def validate(self, data):
        if 'details' in self.initial_data:
            details = self.initial_data.get('details', [])
            if details is not None and len(details) < 1:
                raise serializers.ValidationError({"details": "Ein Angebot muss mindestens 1 Detail enthalten."})
        return data

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            for incoming_detail in details_data:
                offer_type = incoming_detail.get('offer_type')
                if not offer_type:
                    raise serializers.ValidationError({"offer_type": "Offer type is required for each detail in PATCH."})

                try:
                    detail_instance = instance.details.get(offer_type=offer_type)
                except OfferDetail.DoesNotExist:
                    continue

                for attr, value in incoming_detail.items():
                    setattr(detail_instance, attr, value)
                detail_instance.save()

        return instance

    def get_user_details(self, obj):
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'username': obj.user.username
        }