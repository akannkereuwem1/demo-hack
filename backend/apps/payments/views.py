from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class PaymentProcessView(APIView):
    """
    Process a payment for an order.
    """
    def post(self, request):
        return Response({"message": "Payment processing initiated"}, status=status.HTTP_200_OK)

class PaymentWebhookView(APIView):
    """
    Webhook endpoint for Interswitch/payment gateway callbacks.
    """
    def post(self, request):
        return Response({"message": "Webhook received"}, status=status.HTTP_200_OK)
