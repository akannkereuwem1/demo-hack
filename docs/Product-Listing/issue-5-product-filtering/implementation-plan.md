# Issue 5: Add Filtering to Product Feed — Implementation Plan

## Goal
Enable buyers and farmers to filter, search, and sort the product marketplace feed by integrating `django-filter` and DRF filtering backends.

## Changes Made

### `requirements.txt`
- Added `django-filter==24.3`.

### `config/settings.py`
- Added `django_filters` to `INSTALLED_APPS` (below `drf_spectacular`).
- Configured `DEFAULT_FILTER_BACKENDS` to wire up DRF built-in filtering, searching, and ordering across the API globally.

### `products/filters.py` (NEW)
- Implemented `ProductFilter` class extending `django_filters.FilterSet`.
- Mapped specific model fields to filter components:
  - `crop_type` -> `iexact` (case-insensitive exact match)
  - `location` -> `icontains` (substring mapping for addresses)
  - `min_price` -> `gte` (price floor mapping to `price_per_unit`)
  - `max_price` -> `lte` (price ceiling mapping to `price_per_unit`)

### `products/views.py`
- Wired up filtering attributes to `ProductListView`:
  - `filterset_class = ProductFilter`
  - `search_fields = ['title', 'description', 'crop_type']`
  - `ordering_fields = ['price_per_unit', 'created_at']`
  - Default `ordering = ['-created_at']` applied implicitly to keep newest first.

### `tests/test_product_filters.py` (NEW)
- Mapped out exhaustive unit tests for `ProductFilterTests`:
    - Filtering by single characteristics (crop type, location, min/max price bounds).
    - Text search capabilities acting on multiple standard fields.
    - Ascending/descending sorting integration via the `ordering` parameter.
    - Intersected combinations of varying parameters validating the `AND` conjunction logic.

All 65 tests passed.
