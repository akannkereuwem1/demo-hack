from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class OrderListView(APIView):
    """
    List all orders or create a new order.
    """
    def get(self, request):
        return Response([{"id": 1, "status": "pending"}], status=status.HTTP_200_OK)

    def post(self, request):
        return Response({"message": "Order created"}, status=status.HTTP_201_CREATED)

class OrderDetailView(APIView):
    """
    Retrieve, update or delete an order instance.
    """
    def get(self, request, pk):
        return Response({"id": pk, "status": "pending"}, status=status.HTTP_200_OK)
        
    def patch(self, request, pk):
        return Response({"message": f"Order {pk} updated"}, status=status.HTTP_200_OK)
