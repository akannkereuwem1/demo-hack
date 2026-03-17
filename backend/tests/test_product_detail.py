import uuid
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Product, Unit
from users.models import Role, User


class ProductDetailTests(APITestCase):
    """Integration tests for GET /api/products/<uuid>/ (Product Detail)."""

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
        self.product = Product.objects.create(
            farmer=self.farmer,
            title='Test Product',
            description='A test product.',
            crop_type='Maize',
            quantity=Decimal('100.00'),
            unit=Unit.KG,
            price_per_unit=Decimal('200.00'),
            location='Lagos, Nigeria',
            is_available=True,
        )
        self.url = reverse('product-detail', kwargs={'pk': self.product.id})

    def _auth_header(self, user: User) -> dict:
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

    def test_get_product_detail_success(self) -> None:
        """Retrieving an existing product by UUID returns 200 with data."""
        response = self.client.get(self.url, **self._auth_header(self.buyer))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.product.id))
        self.assertEqual(response.data['title'], self.product.title)

    def test_get_nonexistent_product_returns_404(self) -> None:
        """Retrieving a valid UUID that doesn't exist returns 404 json."""
        url = reverse('product-detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.get(url, **self._auth_header(self.buyer))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_get_invalid_uuid_returns_404(self) -> None:
        """A badly formatted UUID fails to match the URL pattern and returns 404 HTML/JSON depending on setup."""
        url = f'/api/products/not-a-uuid/'
        response = self.client.get(url, **self._auth_header(self.buyer))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_product_detail_unauthenticated(self) -> None:
        """Unauthenticated requests are rejected with 401."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
