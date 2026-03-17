# Issue 7: Product Listing Tests (Unit + Integration) — Implementation Plan

## Goal
Build full Product Lifecycle assurance evaluating exact system constraints across creating, retrieving, updating, and deleting standard inventory items. Verify rigorous permissions architecture.

## Changes Made

### `products/permissions.py` (NEW)
- Implemented `IsProductOwnerOrReadOnly` custom permission.
  - Grants any authenticated agent read access (`GET`, `HEAD`, `OPTIONS`).
  - Restricts modification verbs (`PUT`, `PATCH`, `DELETE`) to strictly the product's `farmer` (Owner).

### `products/views.py`
- Upgraded `ProductDetailView` from `RetrieveAPIView` to `RetrieveUpdateDestroyAPIView` specifically to surface Update and Delete logic testing.
- Added `permission_classes = [IsAuthenticated, IsProductOwnerOrReadOnly]`.

### `tests/test_product_lifecycle.py` (NEW)
- Defined `ProductLifecycleTests` integration class modeling end-to-end sessions.
  - **Create:** Farmer creates `Export Quality Cocoa` mapping.
  - **Read (Feed):** Buyer observes the addition in paginated results.
  - **Read (Detail):** Buyer extracts detail UUID constraints successfully.
  - **Protected Update:** Buyer rejected on `PATCH` requests (403), Farmer succeeds patching pricing.
  - **Protected Delete:** Buyer fails to trigger `DELETE` requests (403), Farmer succeeds purging listing (204).
  - **Validation:** Fetches strictly return 404 once deleted. Feed excludes the target securely.

All 71 system tests passed effectively mapping out the complete CRUD boundary block for the Product entity.
