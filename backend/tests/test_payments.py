"""
Payment processing tests.

Property-based tests use Hypothesis with @settings(max_examples=100).
Each property test is tagged:
  # Feature: payment-processing, Property N: <property_text>
"""

import hashlib
import hmac
from unittest.mock import MagicMock, patch

import pytest
import requests
from hypothesis import given, settings
from hypothesis import strategies as st


# ---------------------------------------------------------------------------
# Property 10: Interswitch client raises on non-2xx responses
# ---------------------------------------------------------------------------

class InterswitchClientErrorTests:
    """
    # Feature: payment-processing, Property 10: Interswitch client raises on non-2xx responses
    Validates: Requirements 5.4
    """

    @settings(max_examples=100)
    @given(status_code=st.integers(min_value=400, max_value=599))
    def test_initiate_transaction_raises_on_non_2xx(self, status_code):
        # Feature: payment-processing, Property 10: Interswitch client raises on non-2xx responses
        from apps.payments.interswitch import InterswitchError, initiate_transaction

        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = status_code
        mock_response.text = f"Error {status_code}"

        with patch("apps.payments.interswitch.requests.post", return_value=mock_response):
            with pytest.raises(InterswitchError):
                initiate_transaction("order-123", "5000.00", "ref-abc")

    @settings(max_examples=100)
    @given(status_code=st.integers(min_value=400, max_value=599))
    def test_verify_transaction_raises_on_non_2xx(self, status_code):
        # Feature: payment-processing, Property 10: Interswitch client raises on non-2xx responses
        from apps.payments.interswitch import InterswitchError, verify_transaction

        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = status_code
        mock_response.text = f"Error {status_code}"

        with patch("apps.payments.interswitch.requests.get", return_value=mock_response):
            with pytest.raises(InterswitchError):
                verify_transaction("ref-abc")


# ---------------------------------------------------------------------------
# Django setup for DB-backed property tests
# ---------------------------------------------------------------------------

import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import pytest
from decimal import Decimal
from unittest.mock import MagicMock, call, patch

import django
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase

from hypothesis import given, settings, assume
from hypothesis import strategies as st
from hypothesis.extra.django import TestCase as HypothesisTestCase


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MOCK_INITIATE_RESPONSE = {"responseCode": "00", "checkoutUrl": "https://pay.interswitch.com/checkout/abc"}
MOCK_VERIFY_SUCCESS = {"responseCode": "00", "amount": "500000"}
MOCK_VERIFY_FAILURE = {"responseCode": "99", "message": "Transaction failed"}


def _make_user(role="buyer", email=None):
    from users.models import User
    import uuid
    email = email or f"user-{uuid.uuid4().hex[:8]}@test.com"
    return User.objects.create_user(email=email, password="pass1234", role=role)


def _make_confirmed_order(buyer=None, total_price=Decimal("5000.00")):
    from orders.models import Order
    from users.models import User
    import uuid
    if buyer is None:
        buyer = _make_user(role="buyer")
    farmer = _make_user(role="farmer")
    return Order.objects.create(
        buyer=buyer,
        farmer=farmer,
        status="confirmed",
        total_price=total_price,
    )


# ---------------------------------------------------------------------------
# Property 1: Payment status is always valid
# ---------------------------------------------------------------------------

class PaymentStatusValidityTests(HypothesisTestCase):
    """
    # Feature: payment-processing, Property 1: Payment status is always valid
    Validates: Requirements 1.5, 1.6
    """

    @settings(max_examples=100, deadline=None)
    @given(
        status=st.sampled_from(["pending", "successful", "failed"]),
        total_price=st.decimals(min_value=Decimal("1.00"), max_value=Decimal("999999.99"), places=2),
    )
    def test_payment_status_always_valid(self, status, total_price):
        # Feature: payment-processing, Property 1: Payment status is always valid
        from payments.models import Payment, PaymentStatus
        order = _make_confirmed_order(total_price=total_price)
        payment = Payment.objects.create(
            order=order,
            transaction_reference=f"REF-{order.pk}",
            amount=total_price,
            status=status,
        )
        self.assertIn(payment.status, {
            PaymentStatus.PENDING,
            PaymentStatus.SUCCESSFUL,
            PaymentStatus.FAILED,
        })


# ---------------------------------------------------------------------------
# Property 2: Transaction references are unique
# ---------------------------------------------------------------------------

class TransactionReferenceUniquenessTests(HypothesisTestCase):
    """
    # Feature: payment-processing, Property 2: Transaction references are unique
    Validates: Requirements 1.3
    """

    @settings(max_examples=50, deadline=None)
    @given(n=st.integers(min_value=2, max_value=10))
    def test_transaction_references_are_unique(self, n):
        # Feature: payment-processing, Property 2: Transaction references are unique
        buyer = _make_user(role="buyer")
        references = []

        mock_response = {"responseCode": "00", "checkoutUrl": "https://pay.interswitch.com/x"}

        with patch("payments.interswitch.requests.post") as mock_post:
            mock_post.return_value = MagicMock(ok=True, json=lambda: mock_response)
            from payments.services import initiate_payment
            for _ in range(n):
                order = _make_confirmed_order(buyer=buyer)
                payment = initiate_payment(order.id, buyer)
                references.append(payment.transaction_reference)

        self.assertEqual(len(references), len(set(references)))


# ---------------------------------------------------------------------------
# Property 3: Payment amount matches order total at initiation
# ---------------------------------------------------------------------------

class PaymentAmountMatchesOrderTests(HypothesisTestCase):
    """
    # Feature: payment-processing, Property 3: Payment amount matches order total at initiation
    Validates: Requirements 1.4, 2.1
    """

    @settings(max_examples=100, deadline=None)
    @given(
        total_price=st.decimals(min_value=Decimal("1.00"), max_value=Decimal("999999.99"), places=2),
    )
    def test_payment_amount_matches_order_total(self, total_price):
        # Feature: payment-processing, Property 3: Payment amount matches order total at initiation
        buyer = _make_user(role="buyer")
        order = _make_confirmed_order(buyer=buyer, total_price=total_price)

        mock_response = {"responseCode": "00", "checkoutUrl": "https://pay.interswitch.com/x"}
        with patch("payments.interswitch.requests.post") as mock_post:
            mock_post.return_value = MagicMock(ok=True, json=lambda: mock_response)
            from payments.services import initiate_payment
            payment = initiate_payment(order.id, buyer)

        self.assertEqual(payment.amount, order.total_price)


# ---------------------------------------------------------------------------
# Property 4: Non-confirmed orders are always rejected at initiation
# ---------------------------------------------------------------------------

class NonConfirmedOrderRejectionTests(HypothesisTestCase):
    """
    # Feature: payment-processing, Property 4: Non-confirmed orders are always rejected at initiation
    Validates: Requirements 2.4
    """

    @settings(max_examples=100, deadline=None)
    @given(
        bad_status=st.sampled_from(["pending", "paid", "completed", "declined"]),
    )
    def test_non_confirmed_order_always_rejected(self, bad_status):
        # Feature: payment-processing, Property 4: Non-confirmed orders are always rejected at initiation
        from orders.models import Order
        from payments.models import Payment
        from payments.services import initiate_payment

        buyer = _make_user(role="buyer")
        farmer = _make_user(role="farmer")
        order = Order.objects.create(
            buyer=buyer, farmer=farmer, status=bad_status, total_price=Decimal("1000.00")
        )
        before_count = Payment.objects.count()

        with self.assertRaises(ValidationError):
            initiate_payment(order.id, buyer)

        self.assertEqual(Payment.objects.count(), before_count)


# ---------------------------------------------------------------------------
# Property 5: Duplicate initiation is always rejected
# ---------------------------------------------------------------------------

class DuplicateInitiationRejectionTests(HypothesisTestCase):
    """
    # Feature: payment-processing, Property 5: Duplicate initiation is always rejected
    Validates: Requirements 2.5
    """

    @settings(max_examples=50, deadline=None)
    @given(existing_status=st.sampled_from(["pending", "successful"]))
    def test_duplicate_initiation_always_rejected(self, existing_status):
        # Feature: payment-processing, Property 5: Duplicate initiation is always rejected
        from payments.models import Payment
        from payments.services import initiate_payment

        buyer = _make_user(role="buyer")
        order = _make_confirmed_order(buyer=buyer)

        mock_response = {"responseCode": "00", "checkoutUrl": "https://pay.interswitch.com/x"}
        with patch("payments.interswitch.requests.post") as mock_post:
            mock_post.return_value = MagicMock(ok=True, json=lambda: mock_response)
            first = initiate_payment(order.id, buyer)

        # Force the status to the test scenario
        Payment.objects.filter(pk=first.pk).update(status=existing_status)

        with self.assertRaises(ValidationError):
            with patch("payments.interswitch.requests.post") as mock_post:
                mock_post.return_value = MagicMock(ok=True, json=lambda: mock_response)
                initiate_payment(order.id, buyer)


# ---------------------------------------------------------------------------
# Property 6: mark_as_paid called iff Payment transitions to successful
# ---------------------------------------------------------------------------

class MarkAsPaidConditionTests(HypothesisTestCase):
    """
    # Feature: payment-processing, Property 6: mark_as_paid called iff Payment transitions to successful
    Validates: Requirements 3.2, 4.3, 6.1
    """

    @settings(max_examples=100, deadline=None)
    @given(is_success=st.booleans())
    def test_mark_as_paid_called_iff_successful(self, is_success):
        # Feature: payment-processing, Property 6: mark_as_paid called iff Payment transitions to successful
        from payments.models import Payment, PaymentStatus
        from payments.services import verify_payment

        buyer = _make_user(role="buyer")
        order = _make_confirmed_order(buyer=buyer)
        payment = Payment.objects.create(
            order=order,
            transaction_reference=f"REF-{order.pk}",
            amount=order.total_price,
            status=PaymentStatus.PENDING,
        )

        response_code = "00" if is_success else "99"
        mock_response = {"responseCode": response_code}

        with patch("payments.interswitch.requests.get") as mock_get, \
             patch("payments.services.order_mark_as_paid") as mock_mark:
            mock_get.return_value = MagicMock(ok=True, json=lambda: mock_response)

            if is_success:
                verify_payment(payment.transaction_reference, buyer)
                mock_mark.assert_called_once_with(order.id)
            else:
                with self.assertRaises(ValidationError):
                    verify_payment(payment.transaction_reference, buyer)
                mock_mark.assert_not_called()


# ---------------------------------------------------------------------------
# Property 7: Atomicity — mark_as_paid failure prevents Payment from becoming successful
# ---------------------------------------------------------------------------

class AtomicityTests(HypothesisTestCase):
    """
    # Feature: payment-processing, Property 7: mark_as_paid failure prevents Payment from becoming successful
    Validates: Requirements 6.2, 6.3
    """

    @settings(max_examples=50, deadline=None)
    @given(dummy=st.none())
    def test_mark_as_paid_failure_rolls_back_payment(self, dummy):
        # Feature: payment-processing, Property 7: mark_as_paid failure prevents Payment from becoming successful
        from orders.services import OrderTransitionError
        from payments.models import Payment, PaymentStatus
        from payments.services import verify_payment

        buyer = _make_user(role="buyer")
        order = _make_confirmed_order(buyer=buyer)
        payment = Payment.objects.create(
            order=order,
            transaction_reference=f"REF-{order.pk}",
            amount=order.total_price,
            status=PaymentStatus.PENDING,
        )

        mock_response = {"responseCode": "00"}

        with patch("payments.interswitch.requests.get") as mock_get, \
             patch("payments.services.order_mark_as_paid", side_effect=OrderTransitionError("boom")):
            mock_get.return_value = MagicMock(ok=True, json=lambda: mock_response)
            with self.assertRaises(Exception):
                verify_payment(payment.transaction_reference, buyer)

        payment.refresh_from_db()
        self.assertNotEqual(payment.status, PaymentStatus.SUCCESSFUL)


# ---------------------------------------------------------------------------
# Property 8: Idempotent verification
# ---------------------------------------------------------------------------

class IdempotentVerificationTests(HypothesisTestCase):
    """
    # Feature: payment-processing, Property 8: Idempotent verification
    Validates: Requirements 3.6
    """

    @settings(max_examples=50, deadline=None)
    @given(n=st.integers(min_value=2, max_value=5))
    def test_idempotent_verify_never_calls_interswitch(self, n):
        # Feature: payment-processing, Property 8: Idempotent verification
        from payments.models import Payment, PaymentStatus
        from payments.services import verify_payment

        buyer = _make_user(role="buyer")
        order = _make_confirmed_order(buyer=buyer)
        payment = Payment.objects.create(
            order=order,
            transaction_reference=f"REF-{order.pk}",
            amount=order.total_price,
            status=PaymentStatus.SUCCESSFUL,
        )

        with patch("payments.interswitch.requests.get") as mock_get:
            for _ in range(n):
                result = verify_payment(payment.transaction_reference, buyer)
                self.assertEqual(result.status, PaymentStatus.SUCCESSFUL)
            mock_get.assert_not_called()


# ---------------------------------------------------------------------------
# Property 9: provider_response always populated after Interswitch interaction
# ---------------------------------------------------------------------------

class ProviderResponsePopulatedTests(HypothesisTestCase):
    """
    # Feature: payment-processing, Property 9: provider_response always populated after Interswitch interaction
    Validates: Requirements 3.7, 4.8
    """

    @settings(max_examples=100, deadline=None)
    @given(is_success=st.booleans())
    def test_provider_response_always_populated_after_verify(self, is_success):
        # Feature: payment-processing, Property 9: provider_response always populated after Interswitch interaction
        from payments.models import Payment, PaymentStatus
        from payments.services import verify_payment

        buyer = _make_user(role="buyer")
        order = _make_confirmed_order(buyer=buyer)
        payment = Payment.objects.create(
            order=order,
            transaction_reference=f"REF-{order.pk}",
            amount=order.total_price,
            status=PaymentStatus.PENDING,
        )

        response_code = "00" if is_success else "99"
        mock_response = {"responseCode": response_code, "detail": "some data"}

        with patch("payments.interswitch.requests.get") as mock_get, \
             patch("payments.services.order_mark_as_paid"):
            mock_get.return_value = MagicMock(ok=True, json=lambda: mock_response)
            try:
                verify_payment(payment.transaction_reference, buyer)
            except ValidationError:
                pass  # expected on failure path

        payment.refresh_from_db()
        self.assertTrue(bool(payment.provider_response))
