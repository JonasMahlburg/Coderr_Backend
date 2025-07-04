import django_filters
from rest_framework.exceptions import ValidationError
from offers_app.models import Offer

class OfferFilter(django_filters.FilterSet):
    """
    A FilterSet for the Offer model, allowing filtering by price,
    delivery time, and the creator's ID.
    """
    ALLOWED_FILTERS = {
        'min_price',
        'max_price',
        'min_delivery_time',
        'max_delivery_time',
        'creator_id',
    }

    min_price = django_filters.NumberFilter(method='filter_min_price')
    max_price = django_filters.NumberFilter(method='filter_max_price')
    min_delivery_time = django_filters.NumberFilter(method='filter_min_delivery_time')
    max_delivery_time = django_filters.NumberFilter(method='filter_max_delivery_time')
    creator_id = django_filters.NumberFilter(field_name='user__id')

    def __init__(self, *args, **kwargs):
        """
        Initializes the OfferFilter. Catches TypeError or ValueError during
        initialization and raises a ValidationError.
        """
        try:
            super().__init__(*args, **kwargs)
        except (TypeError, ValueError) as e:
            print(f"DEBUG: OfferFilter initialization error: {e}")
            raise ValidationError({'detail': 'Invalid filter value: ' + str(e)})

    def filter_min_price(self, queryset, name, value):
        """
        Filters offers to include only those with an overall minimum price
        greater than or equal to the specified value.
        Ensures the value is a valid number.
        """
        try:
            float_value = float(value)
        except ValueError:
            raise ValidationError({'min_price': 'Must be a number'})
        return queryset.filter(overall_min_price__gte=float_value)

    def filter_max_price(self, queryset, name, value):
        """
        Filters offers to include only those with an overall minimum price
        less than or equal to the specified value.
        Ensures the value is a valid number.
        """
        try:
            float_value = float(value)
        except ValueError:
            raise ValidationError({'max_price': 'Must be a number'})
        return queryset.filter(overall_min_price__lte=float_value)

    def filter_min_delivery_time(self, queryset, name, value):
        """
        Filters offers to include only those with an overall minimum delivery time
        greater than or equal to the specified value.
        Ensures the value is a valid integer.
        """
        try:
            int_value = int(value)
        except ValueError:
            raise ValidationError({'min_delivery_time': 'Must be an integer'})
        return queryset.filter(overall_min_delivery_time__gte=int_value)

    def filter_max_delivery_time(self, queryset, name, value):
        """
        Filters offers to include only those with an overall minimum delivery time
        less than or equal to the specified value.
        Ensures the value is a valid integer.
        """
        try:
            int_value = int(value)
        except ValueError:
            raise ValidationError({'max_delivery_time': 'Must be an integer'})
        return queryset.filter(overall_min_delivery_time__lte=int_value)

    class Meta:
        """
        Meta class for OfferFilter, defining the model and fields to filter on.
        """
        model = Offer
        fields = [
            'min_price',
            'max_price',
            'min_delivery_time',
            'max_delivery_time',
            'creator_id'
        ]
