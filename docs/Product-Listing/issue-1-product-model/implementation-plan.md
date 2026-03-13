# Issue 1: Create Product Model — Implementation Plan

## Goal
Define the `Product` model in `products/models.py` as the foundation for all product listing features.

## Changes Made

### `products/models.py`
- Added `Unit` TextChoices: `kg`, `tonnes`, `bags`, `crates`, `pieces`
- Added `Product` model with:
  - UUID primary key
  - `farmer` ForeignKey → `users.User` (`CASCADE`, indexed)
  - Fields: `title`, `description`, `crop_type`, `quantity`, `unit`, `price_per_unit`, `location`, `image_url`, `is_available`
  - Timestamps: `created_at` (auto_now_add), `updated_at` (auto_now)
  - `db_table = 'products'`, ordering by `-created_at`
  - Composite index on `(crop_type, location)`

### `products/admin.py`
- Registered `Product` with `ProductAdmin` (list_display, list_filter, search_fields, readonly_fields)

### `products/migrations/0001_initial.py`
- Auto-generated initial migration for the Product model

### `tests/test_product_model.py`
- 12 unit tests covering creation, UUID PK, defaults, FK constraints, cascade delete, timestamps, `__str__`, ordering
