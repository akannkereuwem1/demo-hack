from decimal import Decimal

from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.

    The `farmer` field is read-only and auto-assigned from
    the authenticated request user in the view/service layer.
    """

    farmer_email = serializers.EmailField(source='farmer.email', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'farmer',
            'farmer_email',
            'title',
            'description',
            'crop_type',
            'quantity',
            'unit',
            'price_per_unit',
            'location',
            'image_url',
            'is_available',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'farmer', 'farmer_email', 'created_at', 'updated_at']

    def validate_quantity(self, value: Decimal) -> Decimal:
        """Quantity must be greater than zero."""
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than zero.')
        return value

    def validate_price_per_unit(self, value: Decimal) -> Decimal:
        """Price per unit must be greater than zero."""
        if value <= 0:
            raise serializers.ValidationError('Price per unit must be greater than zero.')
        return value
