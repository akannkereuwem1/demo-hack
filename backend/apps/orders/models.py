import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class OrderStatus(models.TextChoices):
    """Valid statuses for an Order in the AgroNet state machine."""
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    PAID = 'paid', 'Paid'
    COMPLETED = 'completed', 'Completed'
    DECLINED = 'declined', 'Declined'


class Order(models.Model):
    """
    Represents a buyer's request to purchase a product from a farmer.

    Status follows a strict state machine enforced by the service layer:
    pending → confirmed → paid → completed, or pending → declined.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders_as_buyer',
        db_index=True,
    )
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders_as_farmer',
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Order {self.id} [{self.status}] buyer={self.buyer_id}'


class OrderItem(models.Model):
    """
    A line item within an Order.

    Snapshots unit_price from the product at creation time so price changes
    to the product listing do not affect existing orders.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        db_index=True,
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        db_index=True,
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )

    class Meta:
        db_table = 'order_items'

    def __str__(self) -> str:
        return f'OrderItem {self.id} order={self.order_id} product={self.product_id}'
