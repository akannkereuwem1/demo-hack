"""
Payment serializers.

Input serializers validate incoming request data.
Output serializers format Payment responses for the mobile client.
"""

from rest_framework import serializers


class PaymentInitiateSerializer(serializers.Serializer):
    """Input: validate payment initiation request."""

    order_id = serializers.UUIDField()


class PaymentVerifySerializer(serializers.Serializer):
    """Input: validate payment verification request."""

    transaction_reference = serializers.CharField(max_length=100)


class PaymentResponseSerializer(serializers.Serializer):
    """Output: serialize a Payment instance for API responses."""

    transaction_reference = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    status = serializers.CharField()
    order_id = serializers.UUIDField()
    checkout_params = serializers.SerializerMethodField()

    def get_checkout_params(self, obj) -> dict:
        """
        Return Interswitch checkout parameters from provider_response.

        On initiation the provider_response contains the checkout URL/params
        returned by Interswitch. On verification it contains the status payload.
        """
        return obj.provider_response or {}
