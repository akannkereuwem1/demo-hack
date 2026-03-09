# Issue 4: GET /api/products/{id}/ (Product Detail) — Implementation Plan

## Goal
Implement the product details endpoint to allow retrieving full details of a specific product listing using its UUID.

## Changes Made

### `products/urls.py`
- Changed route parameter for `product-detail` from `<int:pk>` (default DRF type) to `<uuid:pk>`. This aligns with the PostgreSQL UUID primary keys used in our database.

### `products/views.py`
- Changed `ProductDetailView` to inherit from `RetrieveAPIView` (previously `APIView`).
- Defined `queryset = Product.objects.all()`. We query base products instead of `is_available=True` so farmers can access and manage their own unavailable listings directly. 
- Declared `serializer_class = ProductSerializer`. Standardizing representation format and allowing DRF to automatically parse UUID parameters into database queries + automatic 404 integration.

### `tests/test_product_detail.py` (NEW)
- Implemented 4 integration test cases simulating success (200), product missing (404), invalid UUID parameter (404 parsing), and anonymous access (401).

All 58 tests passed.
