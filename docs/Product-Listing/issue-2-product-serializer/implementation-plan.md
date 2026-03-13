# Issue 2: Product Serializer & POST /api/products/ — Implementation Plan

## Goal
Enable farmers to create product listings via `POST /api/products/` with proper validation, permissions, and service layer pattern.

## Changes Made

### `products/serializers.py`
- `ProductSerializer` (ModelSerializer) with read-only `id`, `farmer`, `farmer_email`, `created_at`, `updated_at`
- Custom validation: `quantity > 0`, `price_per_unit > 0`

### `products/services.py` (NEW)
- `create_product(farmer, validated_data)` — creates Product with farmer assignment

### `products/views.py`
- `ProductListView.post()` replaced: deserializes input, calls service, returns `201 Created`
- Dynamic permissions: POST requires `IsFarmer`, GET requires `IsAuthenticated`

### `tests/test_product_api.py` (NEW)
- 12 integration tests: success, permission (farmer/buyer/unauth), validation (missing fields, zero/negative values, invalid unit)
