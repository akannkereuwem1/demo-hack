# Issue 3: GET /api/products/ (Marketplace Feed) with Pagination — Walkthrough

## Summary
Refactored the `ProductListView` to serve a paginated feed of available products, relying on DRF's built-in `ListCreateAPIView`.

## Files Changed

| File | Action | Description |
|---|---|---|
| `backend/config/settings.py` | Modified | Added default pagination settings (size 20). |
| `backend/apps/products/views.py` | Modified | Upgraded `ProductListView` from `APIView` to `ListCreateAPIView` with available item filtering. |
| `backend/tests/test_product_feed.py` | New | 6 integration tests targeting the feed endpoint |
| `TASK.md` | Modified | Marked Issue 3 complete |

## Architecture

```
GET /api/products/?page=1
  → ProductListView.get()      [permission: IsAuthenticated]
    → Product.objects.filter(is_available=True)
      → DRF PageNumberPagination limits to 20 products
        → ProductSerializer serializes results
          → 200 OK + Paginated JSON (count, next, previous, results)
```

## Test Results

```
Ran 54 tests in 40.781s — OK
```

- **6 new** product feed tests: all passed
- **48 existing** tests: no regressions (after the `perform_create` patch)
