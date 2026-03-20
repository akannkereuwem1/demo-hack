"""
Payment service layer.

All payment business logic lives here. Views must not contain business logic.
"""

import uuid
from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from orders.models import Order
from orders.services import OrderTransitionError, mark_as_paid as order_mark_as_paid
from users.models import User

from .interswitch import InterswitchError
from .interswitch import initiate_transaction as interswitch_initiate
from .interswitch import validate_webhook_signature
from .interswitch import verify_transaction as interswitch_verify
from .models import Payment, PaymentStatus


def _generate_reference() -> str:
    """Generate a unique transaction reference."""
    return f"AGN-{uuid.uuid4().hex.upper()}"


def initiate_payment(order_id: uuid.UUID, buyer: User) -> Payment:
    """
    Initiate a payment for a confirmed order.

    Args:
        order_id: UUID of the order to pay for.
        buyer: The authenticated buyer making the request.

    Returns:
        The newly created Payment instance (status=pending).

    Raises:
        Http404: If the order does not exist.
        PermissionDenied: If buyer is not the order's buyer.
        ValidationError: If the order is not confirmed, or a payment already exists.
        InterswitchError: If the Interswitch API call fails.
    """
    order: Order = get_object_or_404(Order, pk=order_id)

    if order.buyer_id != buyer.pk:
        raise PermissionDenied("You do not have permission to pay for this order.")

    if order.status != "confirmed":
        raise ValidationError(
            f"Cannot initiate payment: order status is '{order.status}', expected 'confirmed'."
        )

    existing = Payment.objects.filter(
        order=order,
        status__in=[PaymentStatus.PENDING, PaymentStatus.SUCCESSFUL],
    ).first()
    if existing:
        raise ValidationError(
            f"A payment for this order already exists with status '{existing.status}'."
        )

    reference = _generate_reference()

    provider_response = interswitch_initiate(
        order_id=str(order_id),
        amount=order.total_price,
        reference=reference,
    )

    payment = Payment.objects.create(
        order=order,
        transaction_reference=reference,
        amount=order.total_price,
        status=PaymentStatus.PENDING,
        provider_response=provider_response,
    )
    return payment


def verify_payment(transaction_reference: str, buyer: User) -> Payment:
    """
    Verify a payment with Interswitch and update its status.

    Idempotent: if the payment is already successful, returns it without
    re-querying Interswitch.

    Args:
        transaction_reference: The unique reference for the payment.
        buyer: The authenticated buyer making the request.

    Returns:
        The updated Payment instance.

    Raises:
        Http404: If no payment with the given reference exists.
        PermissionDenied: If buyer is not the order's buyer.
        ValidationError: If Interswitch reports the transaction as failed.
    """
    payment: Payment = get_object_or_404(
        Payment, transaction_reference=transaction_reference
    )

    if payment.order.buyer_id != buyer.pk:
        raise PermissionDenied("You do not have permission to verify this payment.")

    # Idempotent: already successful — return without re-querying Interswitch
    if payment.status == PaymentStatus.SUCCESSFUL:
        return payment

    provider_response = interswitch_verify(transaction_reference)

    is_success = _is_interswitch_success(provider_response)

    with transaction.atomic():
        locked: Payment = Payment.objects.select_for_update().get(
            pk=payment.pk
        )
        locked.provider_response = provider_response

        if is_success:
            locked.status = PaymentStatus.SUCCESSFUL
            locked.save(update_fields=["status", "provider_response", "updated_at"])
            order_mark_as_paid(locked.order_id)
        else:
            locked.status = PaymentStatus.FAILED
            locked.save(update_fields=["status", "provider_response", "updated_at"])

    if not is_success:
        raise ValidationError("Payment was not successful according to Interswitch.")

    return locked


def handle_webhook(
    payload: dict,
    raw_body: bytes,
    signature_header: str,
) -> None:
    """
    Process an Interswitch webhook callback.

    Args:
        payload: Parsed JSON body of the webhook.
        raw_body: Raw request body bytes (used for HMAC validation).
        signature_header: Value of the X-Interswitch-Signature header.

    Raises:
        ValidationError: If the HMAC signature is invalid.
    """
    if not validate_webhook_signature(raw_body, signature_header):
        raise ValidationError("Invalid webhook signature.")

    reference = payload.get("transactionReference") or payload.get("transaction_reference")
    if not reference:
        return

    payment = Payment.objects.filter(transaction_reference=reference).first()
    if payment is None:
        # Unknown reference — return silently to prevent Interswitch retry storms
        return

    # Already terminal — idempotent, do nothing
    if payment.status in (PaymentStatus.SUCCESSFUL, PaymentStatus.FAILED):
        return

    is_success = _is_interswitch_success(payload)

    with transaction.atomic():
        locked: Payment = Payment.objects.select_for_update().get(pk=payment.pk)
        locked.provider_response = payload

        if is_success:
            locked.status = PaymentStatus.SUCCESSFUL
            locked.save(update_fields=["status", "provider_response", "updated_at"])
            order_mark_as_paid(locked.order_id)
        else:
            locked.status = PaymentStatus.FAILED
            locked.save(update_fields=["status", "provider_response", "updated_at"])


def _is_interswitch_success(response: dict) -> bool:
    """
    Determine whether an Interswitch response indicates a successful transaction.

    Interswitch uses responseCode '00' to indicate success.
    """
    code = response.get("responseCode") or response.get("response_code", "")
    return str(code) == "00"
