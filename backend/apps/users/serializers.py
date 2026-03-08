from django.contrib.auth import authenticate
from rest_framework import serializers

from users.models import User, Role


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles input validation, role assignment, and secure password hashing.
    """
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    role = serializers.ChoiceField(choices=Role.choices)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'password', 'role']
        read_only_fields = ['id']

    def create(self, validated_data: dict) -> User:
        """Create and return a new user with a securely hashed password."""
        return User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role'],
            full_name=validated_data.get('full_name', ''),
        )


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates credentials and returns the authenticated user.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs: dict) -> dict:
        """Validate email/password and attach the authenticated user to attrs."""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(request=self.context.get('request'), username=email, password=password)

        if not user:
            raise serializers.ValidationError('Invalid email or password. Please try again.')

        if not user.is_active:
            raise serializers.ValidationError('This account has been deactivated.')

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for reading an authenticated user's profile.
    Read-only — used for the GET /api/users/profile/ endpoint.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'created_at', 'updated_at']
        read_only_fields = fields
