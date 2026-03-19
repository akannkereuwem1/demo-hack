"""
Integration tests for the Order Management API.

Covers:
  9.1 - OrderCreationTests         (Requirements 11.1)
  9.2 - OrderStateMachineTests     (Requirements 11.2)
  9.3 - OrderInvalidTransitionTests(Requirements 11.3)
  9.4 - OrderPermissionTests       (Requirements 11.4)
  9.5 - OrderListingIsolationTests (Requirements 11.5)
  9.6 - OrderTotalPriceTests       (Requirements 11.6)
"""

import uuid
from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from orders.models import Order, OrderItem, OrderStatus
from orders.services import mark_as_paid, OrderTransitionError
from products.models import Product, Unit
from users.models import Role, User


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_farmer(email):
    return User.objects.create_user(email=email, password='pass1234', role=Role.FARMER)


def _make_buyer(email):
    return User.objects.create_user(email=email, password='pass1234', role=Role.BUYER)


def _make_product(farmer, price='50.00', available=True):
    return Product.objects.create(
        farmer=farmer,
        title='Test Maize',
        price_per_unit=Decimal(price),
        quantity=Decimal('100.00'),
        unit=Unit.KG,
        crop_type='Maize',
        description='Fresh maize from the farm.',
        location='Lagos, Nigeria',
        is_available=available,
    )


def _make_order(buyer, farmer, product, quantity='2.00', unit_price='50.00', status_val='pending'):
    """Create an Order + OrderItem directly, bypassing the service layer."""
    order = Order.objects.create(
        buyer=buyer,
        farmer=farmer,
        total_price=Decimal(quantity) * Decimal(unit_price),
        status=status_val,
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=Decimal(quantity),
        unit_price=Decimal(unit_price),
    )
    return order


# ---------------------------------------------------------------------------
# 9.1 - OrderCreationTests
# ---------------------------------------------------------------------------

class OrderCreationTests(APITestCase):
    """Integration tests for POST /api/orders/ -- Requirements 11.1"""

    URL = '/api/orders/'

    def setUp(self):
        self.farmer = _make_farmer('farmer@test.com')
        self.buyer = _make_buyer('buyer@test.com')
        self.product = _make_product(self.farmer, price='50.00')

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

    def test_buyer_creates_order_successfully(self):
        """Buyer POSTs a valid order -> 201, status=pending, correct total_price."""
        payload = {'product_id': str(self.product.id), 'quantity': '5.00'}
        response = self.client.post(self.URL, payload, format='json', **self._auth(self.buyer))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(Decimal(response.data['total_price']), Decimal('250.00'))

    def test_unauthenticated_returns_401(self):
        """No auth header -> 401."""
        payload = {'product_id': str(self.product.id), 'quantity': '5.00'}
        response = self.client.post(self.URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_farmer_blocked_returns_403(self):
        """Farmer attempting to create an order -> 403."""
        payload = {'product_id': str(self.product.id), 'quantity': '5.00'}
        response = self.client.post(self.URL, payload, format='json', **self._auth(self.farmer))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_not_found_returns_404(self):
        """Non-existent product UUID -> 404."""
        payload = {'product_id': str(uuid.uuid4()), 'quantity': '5.00'}
        response = self.client.post(self.URL, payload, format='json', **self._auth(self.buyer))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unavailable_product_returns_400(self):
        """Product with is_available=False -> 400."""
        unavailable = _make_product(self.farmer, available=False)
        payload = {'product_id': str(unavailable.id), 'quantity': '5.00'}
        response = self.client.post(self.URL, payload, format='json', **self._auth(self.buyer))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zero_quantity_returns_400(self):
        """quantity=0.00 -> 400."""
        payload = {'product_id': str(self.product.id), 'quantity': '0.00'}
        response = self.client.post(self.URL, payload, format='json', **self._auth(self.buyer))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_quantity_returns_400(self):
        """quantity=-1.00 -> 400."""
        payload = {'product_id': str(self.product.id), 'quantity': '-1.00'}
        response = self.client.post(self.URL, payload, format='json', **self._auth(self.buyer))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# 9.2 - OrderStateMachineTests
# ---------------------------------------------------------------------------

class OrderStateMachineTests(APITestCase):
    """Integration tests for valid state transitions -- Requirements 11.2"""

    def setUp(self):
        self.farmer = _make_farmer('farmer2@test.com')
        self.buyer = _make_buyer('buyer2@test.com')
        self.product = _make_product(self.farmer)

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

    def test_pending_to_confirmed(self):
        """Farmer confirms a pending order -> 200, status=confirmed."""
        order = _make_order(self.buyer, self.farmer, self.product, status_val='pending')
        url = f'/api/orders/{order.id}/confirm/'
        response = self.client.patch(url, format='json', **self._auth(self.farmer))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'confirmed')

    def test_pending_to_declined(self):
        """Farmer declines a pending order -> 200, status=declined."""
        order = _make_order(self.buyer, self.farmer, self.product, status_val='pending')
        url = f'/api/orders/{order.id}/decline/'
        response = self.client.patch(url, format='json', **self._auth(self.farmer))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'declined')

    def test_confirmed_to_paid_via_mark_as_paid(self):
        """mark_as_paid() transitions a confirmed order to paid."""
        order = _make_order(self.buyer, self.farmer, self.product, status_val='confirmed')
        updated = mark_as_paid(order.id)
        self.assertEqual(updated.status, 'paid')

    def test_paid_to_completed(self):
        """Farmer completes a paid order -> 200, status=completed."""
        order = _make_order(self.buyer, self.farmer, self.product, status_val='paid')
        url = f'/api/orders/{order.id}/complete/'
        response = self.client.patch(url, format='json', **self._auth(self.farmer))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')


# ---------------------------------------------------------------------------
# 9.3 - OrderInvalidTransitionTests
# ---------------------------------------------------------------------------

class OrderInvalidTransitionTests(APITestCase):
    """Invalid state transitions must return HTTP 400 -- Requirements 11.3"""

    def setUp(self):
        self.farmer = _make_farmer('farmer3@test.com')
        self.buyer = _make_buyer('buyer3@test.com')
        self.product = _make_product(self.farmer)

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

    def test_confirmed_to_confirmed_returns_400(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='confirmed')
        r = self.client.patch(f'/api/orders/{order.id}/confirm/', format='json', **self._auth(self.farmer))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirmed_to_declined_returns_400(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='confirmed')
        r = self.client.patch(f'/api/orders/{order.id}/decline/', format='json', **self._auth(self.farmer))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_declined_to_confirmed_returns_400(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='declined')
        r = self.client.patch(f'/api/orders/{order.id}/confirm/', format='json', **self._auth(self.farmer))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_paid_to_confirmed_returns_400(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='paid')
        r = self.client.patch(f'/api/orders/{order.id}/confirm/', format='json', **self._auth(self.farmer))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_paid_to_declined_returns_400(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='paid')
        r = self.client.patch(f'/api/orders/{order.id}/decline/', format='json', **self._auth(self.farmer))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_completed_to_confirmed_returns_400(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='completed')
        r = self.client.patch(f'/api/orders/{order.id}/confirm/', format='json', **self._auth(self.farmer))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pending_to_completed_returns_400(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='pending')
        r = self.client.patch(f'/api/orders/{order.id}/complete/', format='json', **self._auth(self.farmer))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mark_as_paid_on_pending_raises_error(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='pending')
        with self.assertRaises(OrderTransitionError):
            mark_as_paid(order.id)

    def test_mark_as_paid_on_completed_raises_error(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='completed')
        with self.assertRaises(OrderTransitionError):
            mark_as_paid(order.id)


# ---------------------------------------------------------------------------
# 9.4 - OrderPermissionTests
# ---------------------------------------------------------------------------

class OrderPermissionTests(APITestCase):
    """Permission enforcement on all order endpoints -- Requirements 11.4"""

    def setUp(self):
        self.farmer = _make_farmer('farmer4@test.com')
        self.other_farmer = _make_farmer('other_farmer4@test.com')
        self.buyer = _make_buyer('buyer4@test.com')
        self.other_buyer = _make_buyer('other_buyer4@test.com')
        self.product = _make_product(self.farmer)

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

    def test_buyer_cannot_confirm_order(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='pending')
        r = self.client.patch(f'/api/orders/{order.id}/confirm/', format='json', **self._auth(self.buyer))
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_buyer_cannot_decline_order(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='pending')
        r = self.client.patch(f'/api/orders/{order.id}/decline/', format='json', **self._auth(self.buyer))
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_buyer_cannot_complete_order(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='paid')
        r = self.client.patch(f'/api/orders/{order.id}/complete/', format='json', **self._auth(self.buyer))
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_owner_farmer_cannot_confirm(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='pending')
        r = self.client.patch(f'/api/orders/{order.id}/confirm/', format='json', **self._auth(self.other_farmer))
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_owner_farmer_cannot_decline(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='pending')
        r = self.client.patch(f'/api/orders/{order.id}/decline/', format='json', **self._auth(self.other_farmer))
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_owner_farmer_cannot_complete(self):
        order = _make_order(self.buyer, self.farmer, self.product, status_val='paid')
        r = self.client.patch(f'/api/orders/{order.id}/complete/', format='json', **self._auth(self.other_farmer))
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_participant_cannot_view_detail(self):
        order = _make_order(self.buyer, self.farmer, self.product)
        r = self.client.get(f'/api/orders/{order.id}/', **self._auth(self.other_buyer))
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_buyer_can_view_own_order_detail(self):
        order = _make_order(self.buyer, self.farmer, self.product)
        r = self.client.get(f'/api/orders/{order.id}/', **self._auth(self.buyer))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_farmer_can_view_own_order_detail(self):
        order = _make_order(self.buyer, self.farmer, self.product)
        r = self.client.get(f'/api/orders/{order.id}/', **self._auth(self.farmer))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_view_detail(self):
        order = _make_order(self.buyer, self.farmer, self.product)
        r = self.client.get(f'/api/orders/{order.id}/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)


# ---------------------------------------------------------------------------
# 9.5 - OrderListingIsolationTests
# ---------------------------------------------------------------------------

class OrderListingIsolationTests(APITestCase):
    """Listing scoping: buyers see only their orders, farmers see only theirs -- Requirements 11.5"""

    URL = '/api/orders/'

    def setUp(self):
        self.farmer_a = _make_farmer('farmer_a5@test.com')
        self.farmer_b = _make_farmer('farmer_b5@test.com')
        self.buyer_a = _make_buyer('buyer_a5@test.com')
        self.buyer_b = _make_buyer('buyer_b5@test.com')
        self.product_a = _make_product(self.farmer_a)
        self.product_b = _make_product(self.farmer_b)
        self.order_a = _make_order(self.buyer_a, self.farmer_a, self.product_a)
        self.order_b = _make_order(self.buyer_b, self.farmer_b, self.product_b)
        self.order_c = _make_order(self.buyer_a, self.farmer_b, self.product_b)

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

    def _ids(self, response):
        return {item['id'] for item in response.data['results']}

    def test_buyer_sees_only_own_orders(self):
        r = self.client.get(self.URL, **self._auth(self.buyer_a))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        ids = self._ids(r)
        self.assertIn(str(self.order_a.id), ids)
        self.assertIn(str(self.order_c.id), ids)
        self.assertNotIn(str(self.order_b.id), ids)

    def test_buyer_b_sees_only_own_orders(self):
        r = self.client.get(self.URL, **self._auth(self.buyer_b))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        ids = self._ids(r)
        self.assertIn(str(self.order_b.id), ids)
        self.assertNotIn(str(self.order_a.id), ids)
        self.assertNotIn(str(self.order_c.id), ids)

    def test_farmer_sees_only_own_orders(self):
        r = self.client.get(self.URL, **self._auth(self.farmer_a))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        ids = self._ids(r)
        self.assertIn(str(self.order_a.id), ids)
        self.assertNotIn(str(self.order_b.id), ids)
        self.assertNotIn(str(self.order_c.id), ids)

    def test_farmer_b_sees_only_own_orders(self):
        r = self.client.get(self.URL, **self._auth(self.farmer_b))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        ids = self._ids(r)
        self.assertIn(str(self.order_b.id), ids)
        self.assertIn(str(self.order_c.id), ids)
        self.assertNotIn(str(self.order_a.id), ids)

    def test_listing_ordered_by_created_at_desc(self):
        r = self.client.get(self.URL, **self._auth(self.buyer_a))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        results = r.data['results']
        self.assertEqual(results[0]['id'], str(self.order_c.id))
        self.assertEqual(results[1]['id'], str(self.order_a.id))

    def test_status_filter_works(self):
        _make_order(self.buyer_a, self.farmer_a, self.product_a, status_val='confirmed')
        r = self.client.get(self.URL + '?status=pending', **self._auth(self.buyer_a))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        for item in r.data['results']:
            self.assertEqual(item['status'], 'pending')


# ---------------------------------------------------------------------------
# 9.6 - OrderTotalPriceTests
# ---------------------------------------------------------------------------

class OrderTotalPriceTests(APITestCase):
    """total_price == quantity x unit_price on creation -- Requirements 11.6"""

    URL = '/api/orders/'

    def setUp(self):
        self.farmer = _make_farmer('farmer6@test.com')
        self.buyer = _make_buyer('buyer6@test.com')

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

    def test_total_price_equals_quantity_times_unit_price(self):
        product = _make_product(self.farmer, price='75.50')
        payload = {'product_id': str(product.id), 'quantity': '4.00'}
        r = self.client.post(self.URL, payload, format='json', **self._auth(self.buyer))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(r.data['total_price']), Decimal('4.00') * Decimal('75.50'))

    def test_total_price_with_fractional_quantity(self):
        product = _make_product(self.farmer, price='10.00')
        payload = {'product_id': str(product.id), 'quantity': '2.50'}
        r = self.client.post(self.URL, payload, format='json', **self._auth(self.buyer))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(r.data['total_price']), Decimal('2.50') * Decimal('10.00'))

    def test_total_price_persisted_in_db(self):
        product = _make_product(self.farmer, price='20.00')
        payload = {'product_id': str(product.id), 'quantity': '3.00'}
        r = self.client.post(self.URL, payload, format='json', **self._auth(self.buyer))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(pk=r.data['id'])
        self.assertEqual(order.total_price, Decimal('3.00') * Decimal('20.00'))

    def test_total_price_unaffected_by_product_price_change(self):
        product = _make_product(self.farmer, price='20.00')
        payload = {'product_id': str(product.id), 'quantity': '3.00'}
        r = self.client.post(self.URL, payload, format='json', **self._auth(self.buyer))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        order_id = r.data['id']
        product.price_per_unit = Decimal('999.00')
        product.save()
        detail = self.client.get(f'/api/orders/{order_id}/', **self._auth(self.buyer))
        self.assertEqual(Decimal(detail.data['total_price']), Decimal('60.00'))
