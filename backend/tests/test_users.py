import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Role, User


# ──────────────────────────────────────────────
# Unit Tests: User Model & UserManager
# ──────────────────────────────────────────────

class UserManagerTests(TestCase):
    """Unit tests for UserManager.create_user and create_superuser."""

    def test_create_user_with_email_and_role(self) -> None:
        """A regular user is created with email, hashed password, and role."""
        user = User.objects.create_user(
            email='farmer@test.com',
            password='securepass123',
            role=Role.FARMER,
        )
        self.assertEqual(user.email, 'farmer@test.com')
        self.assertEqual(user.role, Role.FARMER)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_password_is_hashed(self) -> None:
        """Password must never be stored in plaintext."""
        user = User.objects.create_user(
            email='buyer@test.com',
            password='plaintext123',
            role=Role.BUYER,
        )
        self.assertNotEqual(user.password, 'plaintext123')
        self.assertTrue(user.check_password('plaintext123'))

    def test_uuid_primary_key(self) -> None:
        """User primary key must be a valid UUID."""
        user = User.objects.create_user(
            email='uuid@test.com',
            password='pass1234!',
            role=Role.FARMER,
        )
        self.assertIsInstance(user.id, uuid.UUID)

    def test_create_user_without_email_raises(self) -> None:
        """Creating a user without an email should raise ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='pass1234!', role=Role.BUYER)

    def test_create_superuser(self) -> None:
        """Superusers must have is_staff and is_superuser set to True."""
        admin = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass!',
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_is_farmer_property(self) -> None:
        """is_farmer returns True only for farmers."""
        farmer = User.objects.create_user(email='f@test.com', password='pass1234!', role=Role.FARMER)
        buyer = User.objects.create_user(email='b@test.com', password='pass1234!', role=Role.BUYER)
        self.assertTrue(farmer.is_farmer)
        self.assertFalse(buyer.is_farmer)

    def test_is_buyer_property(self) -> None:
        """is_buyer returns True only for buyers."""
        buyer = User.objects.create_user(email='b2@test.com', password='pass1234!', role=Role.BUYER)
        farmer = User.objects.create_user(email='f2@test.com', password='pass1234!', role=Role.FARMER)
        self.assertTrue(buyer.is_buyer)
        self.assertFalse(farmer.is_buyer)


# ──────────────────────────────────────────────
# Integration Tests: Registration Endpoint
# ──────────────────────────────────────────────

class RegisterViewTests(APITestCase):
    """Integration tests for POST /api/users/register/"""

    URL = reverse_lazy_url = '/api/users/register/'

    def test_register_farmer_successfully(self) -> None:
        """A new farmer can register and receives JWT tokens."""
        payload = {
            'email': 'newfamer@agronet.com',
            'password': 'securepass123',
            'role': 'farmer',
            'full_name': 'Ade Farmer',
        }
        response = self.client.post(self.URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertEqual(response.data['user']['role'], 'farmer')

    def test_register_buyer_successfully(self) -> None:
        """A new buyer can register and receives JWT tokens."""
        payload = {
            'email': 'newbuyer@agronet.com',
            'password': 'securepass123',
            'role': 'buyer',
        }
        response = self.client.post(self.URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['role'], 'buyer')

    def test_register_duplicate_email_fails(self) -> None:
        """Registering with an already-used email should return 400."""
        User.objects.create_user(email='dup@test.com', password='pass1234!', role=Role.FARMER)
        payload = {'email': 'dup@test.com', 'password': 'newpass1234', 'role': 'buyer'}
        response = self.client.post(self.URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_short_password_fails(self) -> None:
        """Passwords shorter than 8 characters should be rejected."""
        payload = {'email': 'short@test.com', 'password': '123', 'role': 'buyer'}
        response = self.client.post(self.URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_role_fails(self) -> None:
        """An invalid role value should be rejected."""
        payload = {'email': 'badrole@test.com', 'password': 'pass1234!', 'role': 'admin'}
        response = self.client.post(self.URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────
# Integration Tests: Login Endpoint
# ──────────────────────────────────────────────

class LoginViewTests(APITestCase):
    """Integration tests for POST /api/users/login/"""

    URL = '/api/users/login/'

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='login@test.com',
            password='correctpass123',
            role=Role.FARMER,
        )

    def test_login_with_valid_credentials(self) -> None:
        """A valid login returns 200 with JWT tokens."""
        payload = {'email': 'login@test.com', 'password': 'correctpass123'}
        response = self.client.post(self.URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])

    def test_login_with_wrong_password(self) -> None:
        """An incorrect password should return 400."""
        payload = {'email': 'login@test.com', 'password': 'wrongpassword'}
        response = self.client.post(self.URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_unknown_email(self) -> None:
        """A non-existent email should return 400."""
        payload = {'email': 'ghost@test.com', 'password': 'somepassword'}
        response = self.client.post(self.URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────
# Integration Tests: Profile Endpoint & RBAC
# ──────────────────────────────────────────────

class ProfileViewTests(APITestCase):
    """Integration tests for GET /api/users/profile/ and RBAC permissions."""

    URL = '/api/users/profile/'

    def setUp(self) -> None:
        self.farmer = User.objects.create_user(
            email='farmerprofile@test.com',
            password='pass1234!',
            role=Role.FARMER,
        )
        self.buyer = User.objects.create_user(
            email='buyerprofile@test.com',
            password='pass1234!',
            role=Role.BUYER,
        )

    def _auth_header(self, user: User) -> dict:
        """Helper to generate a Bearer token header for a given user."""
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

    def test_profile_requires_authentication(self) -> None:
        """An unauthenticated request to /profile/ should return 401."""
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_farmer_can_access_own_profile(self) -> None:
        """An authenticated farmer can fetch their own profile."""
        response = self.client.get(self.URL, **self._auth_header(self.farmer))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.farmer.email)
        self.assertEqual(response.data['role'], 'farmer')

    def test_buyer_can_access_own_profile(self) -> None:
        """An authenticated buyer can fetch their own profile."""
        response = self.client.get(self.URL, **self._auth_header(self.buyer))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'buyer')

    def test_farmer_token_contains_correct_user_id(self) -> None:
        """The JWT token must encode the correct user ID."""
        import jwt
        from django.conf import settings
        token = RefreshToken.for_user(self.farmer)
        decoded = jwt.decode(str(token.access_token), settings.SECRET_KEY, algorithms=['HS256'])
        self.assertEqual(str(decoded['user_id']), str(self.farmer.id))
