import django_filters
from django.db.models import QuerySet

from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    FilterSet for ProductListView.
    Allows exact match for crop_type, string matching for location,
    and range matching for price_per_unit.
    """
    crop_type = django_filters.CharFilter(lookup_expr='iexact')
    location = django_filters.CharFilter(lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name='price_per_unit', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_per_unit', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['crop_type', 'location', 'min_price', 'max_price']
