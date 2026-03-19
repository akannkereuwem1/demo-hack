"""
Serializers for the Order Management feature.

- OrderItemSerializer: read-only nested item representation
- OrderSerializer: full order read serializer with nested items
- OrderCreateSerializer: write serializer for order creation input
"""

from decimal import Decimal

from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for a single OrderItem nested inside an Order response.

    Exposes the product UUID, product title (from the related Product),
    quantity, and the snapshotted unit_price.
    """

    product_id = serializers.UUIDField(source='product.id', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_id', 'product_title', 'quantity', 'unit_price']
        read_only_fields = ['product_id', 'product_title', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    """
    Full read serializer for an Order, including nested OrderItems.

    buyer and farmer are exposed as their UUID values.
    items is a nested list of OrderItemSerializer instances.
    """

    buyer = serializers.UUIDField(source='buyer.id', read_only=True)
    farmer = serializers.UUIDField(source='farmer.id', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'buyer',
            'farmer',
            'status',
            'total_price',
            'note',
            'created_at',
            'updated_at',
            'items',
        ]
        read_only_fields = [
            'id',
            'buyer',
            'farmer',
            'total_price',
            'status',
            'created_at',
            'updated_at',
        ]


class OrderCreateSerializer(serializers.Serializer):
    """
    Write serializer for order creation input.

    Accepts product_id, quantity, and an optional note from the buyer.
    Does not map directly to the Order model — the service layer handles
    object creation using these validated values.
    """

    product_id = serializers.UUIDField()
    quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )
    note = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        default='',
    )
