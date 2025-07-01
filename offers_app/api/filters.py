import django_filters
from django.core.exceptions import ValidationError
from offers_app.models import Offer

class OfferFilter(django_filters.FilterSet):
    """
    FilterSet for Offer model that enables filtering by nested OfferDetail fields.

    Allows the following query parameters:
    - min_price: Filters offers with a minimum price (greater than or equal to).
    - max_price: Filters offers with a maximum price (less than or equal to).
    - min_delivery: Filters offers with a minimum delivery time in days (greater than or equal to).
    - max_delivery: Filters offers with a maximum delivery time in days (less than or equal to).
    """

    min_price = django_filters.NumberFilter(
        field_name='details__price', lookup_expr='gte'
    )
    max_price = django_filters.NumberFilter(
        field_name='details__price', lookup_expr='lte'
    )
    min_delivery = django_filters.NumberFilter(
        field_name='details__delivery_time_in_days', lookup_expr='gte'
    )
    max_delivery = django_filters.NumberFilter(
        field_name='details__delivery_time_in_days', lookup_expr='lte'
    )

    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except (TypeError, ValueError) as e:
            raise ValidationError({'detail': 'Invalid filter value: ' + str(e)})

    class Meta:
        model = Offer
        fields = []