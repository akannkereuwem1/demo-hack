from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class UserProfileView(APIView):
    """
    Base endpoint for User Profiles
    """
    def get(self, request):
        return Response(
            {"message": "User profile endpoint (Mobile API)"},
            status=status.HTTP_200_OK
        )
