# Issue 2: Product Serializer & POST /api/products/ — Walkthrough

## Summary
Implemented the full create product flow: serializer with validation, service layer, and farmer-only permissions.

## Files Changed

| File | Action | Description |
|---|---|---|
| `backend/apps/products/serializers.py` | Modified | `ProductSerializer` with field validation |
| `backend/apps/products/services.py` | New | `create_product()` service function |
| `backend/apps/products/views.py` | Modified | Real `post()` with permissions |
| `backend/tests/test_product_api.py` | New | 12 integration tests |
| `TASK.md` | Modified | Marked Issue 2 complete |

## Architecture

```
POST /api/products/
  → ProductListView.post()     [permission: IsFarmer]
    → ProductSerializer         [validation]
      → services.create_product  [business logic]
        → Product.objects.create [database]
```

## Test Results

```
Ran 48 tests in 27.351s — OK
```

- **12 new** product API tests: all passed
- **36 existing** tests: no regressions
