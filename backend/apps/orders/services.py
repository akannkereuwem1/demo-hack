import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from products.models import Product
from users.models import User

from .models import Order, OrderItem

# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------

VALID_TRANSITIONS: dict[str, list[str]] = {
    "pending":   ["confirmed", "declined"],
    "confirmed": ["paid"],
    "paid":      ["completed"],
}


class OrderTransitionError(ValueError):
    """Raised when an invalid order state transition is attempted."""
    pass


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------

def create_order(
    buyer: User,
    product_id: uuid.UUID,
    quantity: Decimal,
    note: str = "",
) -> Order:
    """
    Create a new Order (and its single OrderItem) atomically.

    Args:
        buyer: The authenticated buyer placing the order.
        product_id: UUID of the product being ordered.
        quantity: Positive decimal quantity to order.
        note: Optional buyer remark (max 500 chars).

    Returns:
        The newly created Order instance.

    Raises:
        Http404: If no Product with the given product_id exists.
        ValidationError: If the product is not currently available.
    """
    product: Product = get_object_or_404(Product, pk=product_id)

    if not product.is_available:
        raise ValidationError("This product is not currently available.")

    unit_price: Decimal = product.price_per_unit
    total_price: Decimal = quantity * unit_price

    with transaction.atomic():
        order = Order.objects.create(
            buyer=buyer,
            farmer=product.farmer,
            total_price=total_price,
            note=note,
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
        )

    return order


def transition_order(order: Order, target_status: str, actor: User) -> Order:
    """
    Transition an order to a new status, enforcing ownership and state machine rules.

    Args:
        order: The Order instance to transition.
        target_status: The desired next status string.
        actor: The user requesting the transition.

    Returns:
        The updated Order instance.

    Raises:
        PermissionError: If actor is not the farmer on the order.
        OrderTransitionError: If the transition is not valid for the current status.
    """
    if actor != order.farmer:
        raise PermissionError("Only the farmer can transition this order.")

    allowed = VALID_TRANSITIONS.get(order.status, [])
    if target_status not in allowed:
        raise OrderTransitionError(
            f"Cannot transition order from '{order.status}' to '{target_status}'."
        )

    with transaction.atomic():
        locked_order: Order = Order.objects.select_for_update().get(pk=order.pk)
        locked_order.status = target_status
        locked_order.save(update_fields=["status", "updated_at"])

    return locked_order


def mark_as_paid(order_id: uuid.UUID) -> Order:
    """
    Transition a confirmed order to 'paid'. Called by the payments module only.

    Args:
        order_id: UUID of the order to mark as paid.

    Returns:
        The updated Order instance.

    Raises:
        Order.DoesNotExist: If no order with the given ID exists.
        OrderTransitionError: If the order is not in 'confirmed' status.
    """
    order: Order = get_object_or_404(Order, pk=order_id)

    if order.status != "confirmed":
        raise OrderTransitionError(
            f"Cannot mark order as paid: current status is '{order.status}'."
        )

    with transaction.atomic():
        locked_order: Order = Order.objects.select_for_update().get(pk=order_id)
        locked_order.status = "paid"
        locked_order.save(update_fields=["status", "updated_at"])

    return locked_order
