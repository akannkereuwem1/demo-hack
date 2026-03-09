from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Product, Unit
from users.models import Role, User


class ProductFilterTests(APITestCase):
    """Integration tests for GET /api/products/ filtering capabilities."""

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

        # Create diverse products for filtering
        self.p1 = self._create_product(
            title='Sweet Cassava',
            description='Fresh and organic cassava roots',
            crop_type='Cassava',
            price_per_unit=Decimal('150.00'),
            location='Ibadan, Nigeria',
        )
        self.p2 = self._create_product(
            title='Yellow Maize',
            description='High quality maize grains',
            crop_type='Maize',
            price_per_unit=Decimal('300.00'),
            location='Kano, Nigeria',
        )
        self.p3 = self._create_product(
            title='White Maize',
            description='Standard white maize',
            crop_type='Maize',
            price_per_unit=Decimal('250.00'),
            location='Ibadan, Nigeria',
        )

    def _auth_header(self, user: User) -> dict:
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

    def _create_product(self, **overrides) -> Product:
        defaults = {
            'farmer': self.farmer,
            'title': 'Test Product',
            'description': 'A test product.',
            'crop_type': 'Maize',
            'quantity': Decimal('100.00'),
            'unit': Unit.KG,
            'price_per_unit': Decimal('200.00'),
            'location': 'Lagos, Nigeria',
            'is_available': True,
        }
        defaults.update(overrides)
        return Product.objects.create(**defaults)

    def test_filter_by_crop_type(self) -> None:
        """Filter by crop_type should return exact (case-insensitive) matches."""
        response = self.client.get(
            f"{self.URL}?crop_type=maize",
            **self._auth_header(self.buyer)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        titles = [p['title'] for p in response.data['results']]
        self.assertIn('Yellow Maize', titles)
        self.assertIn('White Maize', titles)

    def test_filter_by_location(self) -> None:
        """Filter by location should return partial matches."""
        response = self.client.get(
            f"{self.URL}?location=Ibadan",
            **self._auth_header(self.buyer)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        titles = [p['title'] for p in response.data['results']]
        self.assertIn('Sweet Cassava', titles)
        self.assertIn('White Maize', titles)

    def test_filter_by_price_range(self) -> None:
        """Filter by min_price and max_price should bound results."""
        response = self.client.get(
            f"{self.URL}?min_price=200&max_price=260",
            **self._auth_header(self.buyer)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'White Maize')

    def test_search_by_keyword(self) -> None:
        """Search parameter should query title, description, and crop_type."""
        response = self.client.get(
            f"{self.URL}?search=organic",
            **self._auth_header(self.buyer)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Sweet Cassava')

    def test_ordering_by_price_asc(self) -> None:
        """Ordering by price_per_unit ascending."""
        response = self.client.get(
            f"{self.URL}?ordering=price_per_unit",
            **self._auth_header(self.buyer)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [p['price_per_unit'] for p in response.data['results']]
        self.assertEqual(prices, ['150.00', '250.00', '300.00'])

    def test_ordering_by_price_desc(self) -> None:
        """Ordering by -price_per_unit descending."""
        response = self.client.get(
            f"{self.URL}?ordering=-price_per_unit",
            **self._auth_header(self.buyer)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [p['price_per_unit'] for p in response.data['results']]
        self.assertEqual(prices, ['300.00', '250.00', '150.00'])

    def test_combined_filters(self) -> None:
        """Multiple filters should intersect logically (AND)."""
        response = self.client.get(
            f"{self.URL}?location=Ibadan&ordering=-price_per_unit",
            **self._auth_header(self.buyer)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        # In Ibadan, prices are 250 (White Maize) and 150 (Sweet Cassava)
        titles = [p['title'] for p in response.data['results']]
        self.assertEqual(titles, ['White Maize', 'Sweet Cassava'])
