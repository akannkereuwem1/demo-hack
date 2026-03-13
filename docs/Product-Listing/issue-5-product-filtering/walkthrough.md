# Issue 5: Add Filtering to Product Feed — Walkthrough

## Summary
Integrated `django-filter` functionality with Django REST Framework's filtering backends to support detailed marketplace queries.

## Files Changed

| File | Action | Description |
|---|---|---|
| `requirements.txt` | Modified | Pinned `django-filter==24.3`. |
| `backend/config/settings.py` | Modified | Active instantiation of third-party `django_filters` framework. |
| `backend/apps/products/filters.py` | New | Defined `ProductFilter` logic and mappings. |
| `backend/apps/products/views.py` | Modified | Linked filter capabilities directly into `ProductListView`. |
| `backend/tests/test_product_filters.py` | New | Full-range coverage for filtering/searching variations. |
| `TASK.md` | Modified | Marked Issue 5 complete |

## Architecture

```
GET /api/products/?search=organic&location=lagos&ordering=-price_per_unit
  →  IsAuthenticated permission check
    →  Product.objects.filter(is_available=True) [Base Queryset]
      →  DjangoFilterBackend applies `icontains` validation to location
        →  SearchFilter queries `organic` strings across titles/descriptions
          → OrderingFilter aligns remaining rows descending numerically
            →  DRF PageNumberPagination limits payload size
              →  JSON Array returned to Client
```

## Test Results

```
Ran 65 tests in 40.09s — OK
```

- **7 new** product feed filtering tests: all passed
- **58 existing** tests: no regressions. Filtering is fully additive.
