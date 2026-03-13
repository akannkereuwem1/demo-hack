import uuid
from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from products.models import Product, Unit
from users.models import Role, User


class ProductModelTests(TestCase):
    """Unit tests for the Product model."""

    def setUp(self) -> None:
        """Create a farmer user for use across tests."""
        self.farmer = User.objects.create_user(
            email='farmer@test.com',
            password='securepass123',
            role=Role.FARMER,
        )

    def _create_product(self, **overrides) -> Product:
        """Helper to create a product with sensible defaults."""
        defaults = {
            'farmer': self.farmer,
            'title': 'Fresh Maize',
            'description': 'Locally grown organic maize.',
            'crop_type': 'Maize',
            'quantity': Decimal('500.00'),
            'unit': Unit.KG,
            'price_per_unit': Decimal('150.00'),
            'location': 'Lagos, Nigeria',
        }
        defaults.update(overrides)
        return Product.objects.create(**defaults)

    # ── Creation & Defaults ─────────────────────

    def test_create_product_with_required_fields(self) -> None:
        """A product can be created with all required fields."""
        product = self._create_product()
        self.assertEqual(product.title, 'Fresh Maize')
        self.assertEqual(product.crop_type, 'Maize')
        self.assertEqual(product.quantity, Decimal('500.00'))
        self.assertEqual(product.unit, Unit.KG)
        self.assertEqual(product.price_per_unit, Decimal('150.00'))
        self.assertEqual(product.location, 'Lagos, Nigeria')

    def test_uuid_primary_key(self) -> None:
        """Product PK must be a valid UUID, auto-generated."""
        product = self._create_product()
        self.assertIsInstance(product.id, uuid.UUID)

    def test_is_available_defaults_to_true(self) -> None:
        """is_available should default to True when not specified."""
        product = self._create_product()
        self.assertTrue(product.is_available)

    def test_image_url_defaults_to_none(self) -> None:
        """image_url should be None when not provided."""
        product = self._create_product()
        self.assertIsNone(product.image_url)

    # ── Foreign Key ─────────────────────────────

    def test_farmer_fk_links_to_user(self) -> None:
        """The farmer FK should reference the correct User instance."""
        product = self._create_product()
        self.assertEqual(product.farmer, self.farmer)
        self.assertEqual(product.farmer.email, 'farmer@test.com')

    def test_farmer_can_have_multiple_products(self) -> None:
        """A single farmer can own multiple product listings."""
        self._create_product(title='Maize')
        self._create_product(title='Cassava')
        self.assertEqual(self.farmer.products.count(), 2)

    def test_deleting_farmer_cascades_to_products(self) -> None:
        """Deleting a farmer should cascade-delete their products."""
        self._create_product()
        self.assertEqual(Product.objects.count(), 1)
        self.farmer.delete()
        self.assertEqual(Product.objects.count(), 0)

    # ── Timestamps ──────────────────────────────

    def test_created_at_auto_set(self) -> None:
        """created_at should be automatically set on creation."""
        product = self._create_product()
        self.assertIsNotNone(product.created_at)

    def test_updated_at_auto_set(self) -> None:
        """updated_at should be automatically set on creation."""
        product = self._create_product()
        self.assertIsNotNone(product.updated_at)

    def test_updated_at_changes_on_save(self) -> None:
        """updated_at should change when the product is saved again."""
        product = self._create_product()
        original_updated = product.updated_at
        product.title = 'Updated Maize'
        product.save()
        product.refresh_from_db()
        self.assertGreater(product.updated_at, original_updated)

    # ── String Representation ───────────────────

    def test_str_representation(self) -> None:
        """__str__ should return a human-readable summary."""
        product = self._create_product()
        expected = 'Fresh Maize — Maize (500.00 kg)'
        self.assertEqual(str(product), expected)

    # ── Ordering ────────────────────────────────

    def test_default_ordering_is_newest_first(self) -> None:
        """Products should be ordered by -created_at by default."""
        p1 = self._create_product(title='First')
        p2 = self._create_product(title='Second')
        products = list(Product.objects.all())
        self.assertEqual(products[0], p2)
        self.assertEqual(products[1], p1)
