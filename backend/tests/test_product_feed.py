from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Product, Unit
from users.models import Role, User


class ProductFeedTests(APITestCase):
    """Integration tests for GET /api/products/ (Marketplace Feed)."""

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
        }
        defaults.update(overrides)
        return Product.objects.create(**defaults)

    # ── Basic Feed ──────────────────────────────

    def test_feed_returns_paginated_json(self) -> None:
        """Response should contain count, next, previous, results."""
        self._create_product()
        response = self.client.get(self.URL, **self._auth_header(self.buyer))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

    def test_empty_feed_returns_empty_results(self) -> None:
        """An empty marketplace should return count=0 and empty results."""
        response = self.client.get(self.URL, **self._auth_header(self.buyer))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])

    # ── Filtering by Availability ───────────────

    def test_feed_excludes_unavailable_products(self) -> None:
        """Only is_available=True products should appear in the feed."""
        self._create_product(title='Available', is_available=True)
        self._create_product(title='Sold Out', is_available=False)
        response = self.client.get(self.URL, **self._auth_header(self.buyer))
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Available')

    # ── Ordering ────────────────────────────────

    def test_feed_ordered_newest_first(self) -> None:
        """Products should be ordered by -created_at (newest first)."""
        self._create_product(title='First')
        self._create_product(title='Second')
        response = self.client.get(self.URL, **self._auth_header(self.buyer))
        titles = [p['title'] for p in response.data['results']]
        self.assertEqual(titles, ['Second', 'First'])

    # ── Pagination ──────────────────────────────

    def test_pagination_splits_results(self) -> None:
        """With PAGE_SIZE=20, 25 products should split across 2 pages."""
        for i in range(25):
            self._create_product(title=f'Product {i}')
        response = self.client.get(self.URL, **self._auth_header(self.buyer))
        self.assertEqual(response.data['count'], 25)
        self.assertEqual(len(response.data['results']), 20)
        self.assertIsNotNone(response.data['next'])

        # Page 2
        response_p2 = self.client.get(
            self.URL, {'page': 2}, **self._auth_header(self.buyer),
        )
        self.assertEqual(len(response_p2.data['results']), 5)
        self.assertIsNone(response_p2.data['next'])

    # ── Auth Required ───────────────────────────

    def test_unauthenticated_user_gets_401(self) -> None:
        """Unauthenticated request should return 401."""
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
