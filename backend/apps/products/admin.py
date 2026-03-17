from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for the Product model."""

    list_display = (
        'title',
        'crop_type',
        'quantity',
        'unit',
        'price_per_unit',
        'location',
        'is_available',
        'farmer',
        'created_at',
    )
    list_filter = ('crop_type', 'unit', 'is_available', 'location')
    search_fields = ('title', 'description', 'crop_type', 'location')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
