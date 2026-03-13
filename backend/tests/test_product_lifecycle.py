from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Product, Unit
from users.models import Role, User


class ProductLifecycleTests(APITestCase):
    """
    End-to-End integration tests covering the full Product lifecycle:
    Create -> List -> Detail -> Update -> Delete
    """

    def setUp(self) -> None:
        self.farmer = User.objects.create_user(
            email='farmer_producer@test.com',
            password='securepass123',
            role=Role.FARMER,
        )
        self.buyer = User.objects.create_user(
            email='buyer_consumer@test.com',
            password='securepass123',
            role=Role.BUYER,
        )
        self.list_url = '/api/products/'

    def _auth_header(self, user: User) -> dict:
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

    def test_full_product_lifecycle(self) -> None:
        """
        Simulates an end-to-end user session involving product creation, 
        browsing, protected modifications, and final deletion.
        """

        # -----------------------------------------------------------------
        # STEP 1: CREATE (Farmer creates a new product listing)
        # -----------------------------------------------------------------
        create_payload = {
            'title': 'Export Quality Cocoa',
            'description': 'Premium dried cocoa beans',
            'crop_type': 'Cocoa',
            'quantity': '500.00',
            'unit': Unit.KG,
            'price_per_unit': '1200.00',
            'location': 'Ondo, Nigeria',
            'is_available': True
        }
        create_response = self.client.post(
            self.list_url,
            create_payload,
            format='json',
            **self._auth_header(self.farmer)
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        product_id = create_response.data['id']
        detail_url = f'/api/products/{product_id}/'

        # -----------------------------------------------------------------
        # STEP 2: LIST (Buyer verifies the product appears in the feed)
        # -----------------------------------------------------------------
        list_response = self.client.get(
            f"{self.list_url}?search=Cocoa",
            **self._auth_header(self.buyer)
        )
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        # Verify the newly created product is in the results
        self.assertTrue(any(p['id'] == product_id for p in list_response.data['results']))

        # -----------------------------------------------------------------
        # STEP 3: DETAIL (Buyer views specific product details)
        # -----------------------------------------------------------------
        detail_response = self.client.get(
            detail_url,
            **self._auth_header(self.buyer)
        )
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['title'], 'Export Quality Cocoa')

        # -----------------------------------------------------------------
        # STEP 4.1: UPDATE - UNAUTHORIZED (Buyer tries to change the price)
        # -----------------------------------------------------------------
        unauth_update_response = self.client.patch(
            detail_url,
            {'price_per_unit': '500.00'},
            format='json',
            **self._auth_header(self.buyer)
        )
        self.assertEqual(unauth_update_response.status_code, status.HTTP_403_FORBIDDEN)

        # -----------------------------------------------------------------
        # STEP 4.2: UPDATE - AUTHORIZED (Farmer updates their own price/quantity)
        # -----------------------------------------------------------------
        auth_update_response = self.client.patch(
            detail_url,
            {'price_per_unit': '1100.00', 'quantity': '450.00'},
            format='json',
            **self._auth_header(self.farmer)
        )
        self.assertEqual(auth_update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(auth_update_response.data['price_per_unit'], '1100.00')
        self.assertEqual(auth_update_response.data['quantity'], '450.00')

        # -----------------------------------------------------------------
        # STEP 5.1: DELETE - UNAUTHORIZED (Buyer tries to delete the listing)
        # -----------------------------------------------------------------
        unauth_delete_response = self.client.delete(
            detail_url,
            **self._auth_header(self.buyer)
        )
        self.assertEqual(unauth_delete_response.status_code, status.HTTP_403_FORBIDDEN)

        # -----------------------------------------------------------------
        # STEP 5.2: DELETE - AUTHORIZED (Farmer removes their listing)
        # -----------------------------------------------------------------
        auth_delete_response = self.client.delete(
            detail_url,
            **self._auth_header(self.farmer)
        )
        self.assertEqual(auth_delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # -----------------------------------------------------------------
        # STEP 6: VERIFY DELETION
        # -----------------------------------------------------------------
        # Try fetching detail view, expect 404
        missing_detail_response = self.client.get(
            detail_url,
            **self._auth_header(self.buyer)
        )
        self.assertEqual(missing_detail_response.status_code, status.HTTP_404_NOT_FOUND)

        # Ensure feed does not return it either
        clean_list_response = self.client.get(
            self.list_url,
            **self._auth_header(self.buyer)
        )
        self.assertFalse(any(p['id'] == product_id for p in clean_list_response.data['results']))
