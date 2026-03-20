"""
Payment views.

Views contain no business logic — they parse requests, enforce permissions,
delegate to Payment_Service, and return serialized responses.
"""

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsBuyer
from .serializers import (
    PaymentInitiateSerializer,
    PaymentResponseSerializer,
    PaymentVerifySerializer,
)
from .services import handle_webhook, initiate_payment, verify_payment


class PaymentInitiateView(APIView):
    """
    POST /api/payments/initiate/

    Initiate a payment for a confirmed order.
    Requires JWT authentication and buyer role.
    Returns 201 with transaction reference and Interswitch checkout params.
    """

    permission_classes = [IsAuthenticated, IsBuyer]

    @extend_schema(
        request=PaymentInitiateSerializer,
        responses={201: PaymentResponseSerializer},
        summary="Initiate a payment",
        description="Initiate a payment for a confirmed order. Returns transaction reference and Interswitch checkout params.",
    )
    def post(self, request):
        serializer = PaymentInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = initiate_payment(
            order_id=serializer.validated_data["order_id"],
            buyer=request.user,
        )

        return Response(
            PaymentResponseSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


class PaymentVerifyView(APIView):
    """
    POST /api/payments/verify/

    Verify a payment outcome with Interswitch.
    Requires JWT authentication and buyer role.
    Returns 200 with updated payment status.
    """

    permission_classes = [IsAuthenticated, IsBuyer]

    @extend_schema(
        request=PaymentVerifySerializer,
        responses={200: PaymentResponseSerializer},
        summary="Verify a payment",
        description="Verify a payment outcome with Interswitch and update its status.",
    )
    def post(self, request):
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = verify_payment(
            transaction_reference=serializer.validated_data["transaction_reference"],
            buyer=request.user,
        )

        return Response(
            PaymentResponseSerializer(payment).data,
            status=status.HTTP_200_OK,
        )


class PaymentWebhookView(APIView):
    """
    POST /api/payments/webhook/

    Receive Interswitch webhook callbacks.
    No JWT authentication — validated via HMAC signature only.
    Always returns 200 to prevent Interswitch retry storms.
    """

    authentication_classes = []
    permission_classes = []

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="Webhook received successfully")},
        summary="Interswitch webhook callback",
        description="Receives Interswitch webhook callbacks. Authenticated via HMAC signature header X-Interswitch-Signature.",
    )
    def post(self, request):
        raw_body: bytes = request.body
        signature_header: str = request.headers.get("X-Interswitch-Signature", "")

        handle_webhook(
            payload=request.data,
            raw_body=raw_body,
            signature_header=signature_header,
        )

        return Response({"success": True}, status=status.HTTP_200_OK)
