from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ImageClassificationView(APIView):
    """
    Classify an agricultural image.
    """
    def post(self, request):
        return Response({"classification": "Tomato_Blight"}, status=status.HTTP_200_OK)

class PricePredictionView(APIView):
    """
    Predict price for agricultural produce based on market trends.
    """
    def post(self, request):
        return Response({"predicted_price": 500.00}, status=status.HTTP_200_OK)
