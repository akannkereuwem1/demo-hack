import uuid

from django.conf import settings
from django.db import models


class Unit(models.TextChoices):
    """Supported measurement units for product quantities."""
    KG = 'kg', 'Kilograms'
    TONNES = 'tonnes', 'Tonnes'
    BAGS = 'bags', 'Bags'
    CRATES = 'crates', 'Crates'
    PIECES = 'pieces', 'Pieces'


class Product(models.Model):
    """
    Represents an agricultural product listing on the AgroNet marketplace.

    Only users with the 'farmer' role should create listings.
    Uses UUID as primary key per project database rules.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        db_index=True,
        help_text='The farmer who owns this listing.',
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    crop_type = models.CharField(max_length=100, db_index=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.CharField(
        max_length=20,
        choices=Unit.choices,
        default=Unit.KG,
    )
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=255, db_index=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    is_available = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['crop_type', 'location'], name='idx_crop_location'),
        ]

    def __str__(self) -> str:
        return f'{self.title} — {self.crop_type} ({self.quantity} {self.unit})'
