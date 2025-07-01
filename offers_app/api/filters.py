# offers_app/filters.py
import django_filters
from rest_framework.exceptions import ValidationError
from offers_app.models import Offer

class OfferFilter(django_filters.FilterSet):
 
    min_price = django_filters.NumberFilter(method='filter_min_price')
    max_price = django_filters.NumberFilter(method='filter_max_price')
    min_delivery = django_filters.NumberFilter(method='filter_min_delivery')
    max_delivery = django_filters.NumberFilter(method='filter_max_delivery')

    def filter_min_price(self, queryset, name, value):
        try:
            float_value = float(value)
        except ValueError:
            raise ValidationError({'min_price': 'Must be a number'})
        return queryset.filter(overall_min_price__gte=float_value)

    def filter_max_price(self, queryset, name, value):
        try:
            float_value = float(value)
        except ValueError:
            raise ValidationError({'max_price': 'Must be a number'})
        return queryset.filter(overall_min_price__lte=float_value)

    def filter_min_delivery(self, queryset, name, value):
        try:
            int_value = int(value)
        except ValueError:
            raise ValidationError({'min_delivery': 'Must be an integer'})
        return queryset.filter(overall_min_delivery_time__gte=int_value)

    def filter_max_delivery(self, queryset, name, value):
        try:
            int_value = int(value)
        except ValueError:
            raise ValidationError({'max_delivery': 'Must be an integer'})
        return queryset.filter(overall_min_delivery_time__lte=int_value)

    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except (TypeError, ValueError) as e:
         
            print(f"DEBUG: OfferFilter initialization error: {e}")
            raise ValidationError({'detail': 'Invalid filter value: ' + str(e)})

    class Meta:
        model = Offer
        fields = []