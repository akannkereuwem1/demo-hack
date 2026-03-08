from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ProductListView(APIView):
    """
    List all products or create a new product.
    """
    def get(self, request):
        return Response([{"id": 1, "name": "Sample Product"}], status=status.HTTP_200_OK)
        
    def post(self, request):
        return Response({"message": "Product created"}, status=status.HTTP_201_CREATED)

class ProductDetailView(APIView):
    """
    Retrieve, update or delete a product instance.
    """
    def get(self, request, pk):
        return Response({"id": pk, "name": "Sample Product"}, status=status.HTTP_200_OK)
