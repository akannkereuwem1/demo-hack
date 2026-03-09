from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Product, Unit
from users.models import Role, User


class ProductCreateAPITests(APITestCase):
    """Integration tests for POST /api/products/"""

    URL = '/api/products/'

    def setUp(self) -> None:
        self.farmer = User.objects.create_user(
            email='farmer@test.com',
            password='securepass123',
            role=Role.FARMER,
        )
        self.buyer = User.objects.create_user(
            email='buyer@test.com',
            password='securepass123',
            role=Role.BUYER,
        )
        self.valid_payload = {
            'title': 'Fresh Tomatoes',
            'description': 'Organic tomatoes from the farm.',
            'crop_type': 'Tomatoes',
            'quantity': '200.00',
            'unit': 'kg',
            'price_per_unit': '350.00',
            'location': 'Ibadan, Nigeria',
        }

    def _auth_header(self, user: User) -> dict:
        """Helper to generate a Bearer token header for a given user."""
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

    # ── Success Cases ───────────────────────────

    def test_farmer_creates_product_successfully(self) -> None:
        """A farmer can create a product and gets 201 with product data."""
        response = self.client.post(
            self.URL, self.valid_payload, format='json',
            **self._auth_header(self.farmer),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Fresh Tomatoes')
        self.assertEqual(response.data['crop_type'], 'Tomatoes')
        self.assertEqual(response.data['unit'], 'kg')
        self.assertEqual(Product.objects.count(), 1)

    def test_farmer_auto_assigned_from_token(self) -> None:
        """The farmer field should be auto-assigned from request.user, not the payload."""
        response = self.client.post(
            self.URL, self.valid_payload, format='json',
            **self._auth_header(self.farmer),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(response.data['farmer']), str(self.farmer.id))
        self.assertEqual(response.data['farmer_email'], self.farmer.email)

    def test_is_available_defaults_to_true(self) -> None:
        """is_available should default to True if not provided."""
        response = self.client.post(
            self.URL, self.valid_payload, format='json',
            **self._auth_header(self.farmer),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_available'])

    # ── Permission Cases ────────────────────────

    def test_buyer_cannot_create_product(self) -> None:
        """A buyer should receive 403 Forbidden when trying to create."""
        response = self.client.post(
            self.URL, self.valid_payload, format='json',
            **self._auth_header(self.buyer),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_create(self) -> None:
        """An unauthenticated request should return 401."""
        response = self.client.post(self.URL, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ── Validation Cases ────────────────────────

    def test_missing_title_returns_400(self) -> None:
        """Missing required field 'title' should return 400."""
        payload = {**self.valid_payload}
        del payload['title']
        response = self.client.post(
            self.URL, payload, format='json',
            **self._auth_header(self.farmer),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_description_returns_400(self) -> None:
        """Missing required field 'description' should return 400."""
        payload = {**self.valid_payload}
        del payload['description']
        response = self.client.post(
            self.URL, payload, format='json',
            **self._auth_header(self.farmer),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zero_quantity_returns_400(self) -> None:
        """Quantity of 0 should be rejected."""
        payload = {**self.valid_payload, 'quantity': '0.00'}
        response = self.client.post(
            self.URL, payload, format='json',
            **self._auth_header(self.farmer),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_quantity_returns_400(self) -> None:
        """Negative quantity should be rejected."""
        payload = {**self.valid_payload, 'quantity': '-10.00'}
        response = self.client.post(
            self.URL, payload, format='json',
            **self._auth_header(self.farmer),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zero_price_returns_400(self) -> None:
        """Price per unit of 0 should be rejected."""
        payload = {**self.valid_payload, 'price_per_unit': '0.00'}
        response = self.client.post(
            self.URL, payload, format='json',
            **self._auth_header(self.farmer),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_price_returns_400(self) -> None:
        """Negative price per unit should be rejected."""
        payload = {**self.valid_payload, 'price_per_unit': '-50.00'}
        response = self.client.post(
            self.URL, payload, format='json',
            **self._auth_header(self.farmer),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_unit_returns_400(self) -> None:
        """An invalid unit choice should be rejected."""
        payload = {**self.valid_payload, 'unit': 'gallons'}
        response = self.client.post(
            self.URL, payload, format='json',
            **self._auth_header(self.farmer),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
