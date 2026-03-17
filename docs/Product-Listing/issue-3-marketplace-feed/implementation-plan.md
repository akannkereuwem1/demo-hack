# Issue 3: GET /api/products/ (Marketplace Feed) with Pagination — Implementation Plan

## Goal
Enable buyers and farmers to browse available products using pagination. Replace the existing `get()` stub in `ProductListView`.

## Changes Made

### `config/settings.py`
- Added `DEFAULT_PAGINATION_CLASS`: `PageNumberPagination` to `REST_FRAMEWORK`
- Set `PAGE_SIZE` to 20

### `products/views.py`
- Changed `ProductListView` from `APIView` to `ListCreateAPIView` to enable DRY automatic list behavior
- Added `queryset = Product.objects.filter(is_available=True)`
- Added `serializer_class = ProductSerializer`
- Implemented `perform_create()` to retain the Issue #2 business logic delegation to `services.create_product()`
- Assigned `serializer.instance = product` in `perform_create()` to ensure correct JSON serialization of the 201 response.

### `tests/test_product_feed.py` (NEW)
- 6 integration tests: success, pagination format (count, next, previous, results), is_available=True filtering, ordering, large pagination split, unauthenticated access rejection.
- All 54 tests pass.
