from typing import Any

from .models import Product


def create_product(farmer: Any, validated_data: dict) -> Product:
    """
    Create a new product listing for the given farmer.

    Args:
        farmer: The authenticated User instance (must have role='farmer').
        validated_data: Dictionary of validated fields from ProductSerializer.

    Returns:
        The newly created Product instance.
    """
    return Product.objects.create(farmer=farmer, **validated_data)
