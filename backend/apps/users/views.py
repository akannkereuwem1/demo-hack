import logging

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from users.serializers import UserLoginSerializer, UserProfileSerializer, UserRegistrationSerializer

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """
    POST /api/users/register/
    Public endpoint to create a new farmer or buyer account.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: UserProfileSerializer},
        description="Public endpoint to create a new farmer or buyer account."
    )
    def post(self, request: Request) -> Response:
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for the newly registered user
        refresh = RefreshToken.for_user(user)

        logger.info(f'New user registered: {user.email} (role={user.role})')

        return Response(
            {
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/users/login/
    Public endpoint to authenticate a user and return JWT tokens.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserLoginSerializer,
        responses={200: UserProfileSerializer},
        description="Public endpoint to authenticate a user and return JWT tokens."
    )
    def post(self, request: Request) -> Response:
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        logger.info(f'User logged in: {user.email}')

        return Response(
            {
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    """
    GET /api/users/profile/
    Protected endpoint to fetch the authenticated user's profile.
    Requires a valid JWT Bearer token in the Authorization header.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserProfileSerializer},
        description="Protected endpoint to fetch the authenticated user's profile."
    )
    def get(self, request: Request) -> Response:
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
