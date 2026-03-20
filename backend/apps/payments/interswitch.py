"""
Interswitch HTTP client.

All outbound calls to the Interswitch API are isolated here.
Credentials are read exclusively from environment variables — never hardcoded.
"""

import hashlib
import hmac
import os
from decimal import Decimal

import requests


class InterswitchError(Exception):
    """Raised when the Interswitch API returns a non-2xx HTTP response."""


def _get_base_url() -> str:
    return os.environ.get("INTERSWITCH_BASE_URL", "")


def _get_auth_headers() -> dict:
    """Build request headers using credentials from environment variables only."""
    client_id = os.environ.get("INTERSWITCH_CLIENT_ID", "")
    client_secret = os.environ.get("INTERSWITCH_CLIENT_SECRET", "")
    return {
        "Content-Type": "application/json",
        "client_id": client_id,
        "client_secret": client_secret,
    }


def initiate_transaction(order_id: str, amount: Decimal, reference: str) -> dict:
    """
    Initiate a payment transaction with Interswitch.

    POSTs to {INTERSWITCH_BASE_URL}/api/v2/purchases.

    Args:
        order_id: The AgroNet order identifier.
        amount: The transaction amount (in the smallest currency unit or as a Decimal).
        reference: A unique transaction reference string.

    Returns:
        The parsed JSON response from Interswitch as a dict.

    Raises:
        InterswitchError: If Interswitch returns a non-2xx HTTP status code.
    """
    base_url = _get_base_url()
    url = f"{base_url}/api/v2/purchases"
    payload = {
        "merchantCode": os.environ.get("INTERSWITCH_CLIENT_ID", ""),
        "payableCode": reference,
        "amount": str(amount),
        "redirectUrl": "",
        "currencyCode": "566",  # NGN
        "customerId": order_id,
        "customerName": order_id,
        "transactionReference": reference,
    }
    headers = _get_auth_headers()
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    if not response.ok:
        raise InterswitchError(
            f"Interswitch initiate_transaction failed: "
            f"HTTP {response.status_code} — {response.text}"
        )
    return response.json()


def verify_transaction(reference: str) -> dict:
    """
    Verify a transaction status with Interswitch.

    GETs transaction status from {INTERSWITCH_BASE_URL}/api/v2/purchases/{reference}.

    Args:
        reference: The unique transaction reference to look up.

    Returns:
        The parsed JSON response from Interswitch as a dict.

    Raises:
        InterswitchError: If Interswitch returns a non-2xx HTTP status code.
    """
    base_url = _get_base_url()
    url = f"{base_url}/api/v2/purchases/{reference}"
    headers = _get_auth_headers()
    response = requests.get(url, headers=headers, timeout=30)
    if not response.ok:
        raise InterswitchError(
            f"Interswitch verify_transaction failed: "
            f"HTTP {response.status_code} — {response.text}"
        )
    return response.json()


def validate_webhook_signature(payload: bytes, signature_header: str) -> bool:
    """
    Validate an Interswitch webhook HMAC-SHA512 signature.

    Computes HMAC-SHA512 of `payload` using INTERSWITCH_CLIENT_SECRET and
    compares to `signature_header` using a constant-time comparison to
    prevent timing attacks.

    Args:
        payload: The raw request body bytes.
        signature_header: The signature value from the X-Interswitch-Signature header.

    Returns:
        True if the signature is valid, False otherwise.
    """
    client_secret = os.environ.get("INTERSWITCH_CLIENT_SECRET", "")
    expected = hmac.new(
        client_secret.encode("utf-8"),
        payload,
        hashlib.sha512,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)
