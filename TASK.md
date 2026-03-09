# TASK.md — Next Issues for Product Listings

## Current State (Post Issue #18)

Issue #18 (Refactoring to Mobile Backend API) is **resolved**. The products app currently has:

- **`models.py`** — Empty (no Product model yet).
- **`views.py`** — Placeholder stub views returning hardcoded JSON.
- **`serializers.py`** — Empty scaffold.
- **`urls.py`** — Routes to stubs at `api/products/` and `api/products/<pk>/`.

The foundation (DRF, JWT auth, UUID-based User model with `farmer`/`buyer` roles, bcrypt hashing, `drf-spectacular`) is fully in place. The issues below build on top of that.

---

## Recommended Issues (In Order)

### Issue 1: Create Product Model

> **Why first:** Everything else depends on a real database model.

**Scope:**

- [x] Define `Product` model in `products/models.py` with UUID primary key
- [x] Fields: `title`, `description`, `crop_type`, `quantity`, `unit` (kg, tonnes, etc.), `price_per_unit`, `location`, `image_url`, `is_available`
- [x] `farmer` ForeignKey to custom `User` model (only farmers can list)
- [x] Timestamps: `created_at`, `updated_at`
- [x] Add `db_table = 'products'` and relevant indexes
- [x] Generate and apply migrations
- [x] Register model in `products/admin.py`

**Files:** `products/models.py`, `products/admin.py`, `products/migrations/`

---

### Issue 2: Implement Product Serializer & POST /api/products/ (Create Listing)

> **Why second:** Farmers need the ability to create listings before buyers can browse.

**Scope:**

- [x] Create `ProductSerializer` in `products/serializers.py` (validate all fields, auto-assign `farmer` from `request.user`)
- [x] Replace stub `post()` in `ProductListView` with real create logic using the service layer pattern
- [x] Create `products/services.py` for business logic (views call services, per AGENTS.md Rule 6)
- [x] Enforce permission: only users with `role=farmer` can create products
- [x] Return created product JSON with `201 Created`


**Files:** `products/serializers.py`, `products/views.py`, `products/services.py`, `tests/`

---

### Issue 3: Implement GET /api/products/ (Marketplace Feed) with Pagination

> **Why combined:** Pagination is part of a well-implemented list endpoint, not a separate feature. DRF makes this easy to add at the same time.

**Scope:**

- [x] Replace stub `get()` in `ProductListView` with real queryset (only `is_available=True`)
- [x] Configure `DEFAULT_PAGINATION_CLASS` and `PAGE_SIZE` in `settings.py` (e.g., `PageNumberPagination`, 20 per page)
- [x] Return paginated product list JSON


**Files:** `products/views.py`, `config/settings.py`, `tests/`

---

### Issue 4: Implement GET /api/products/{id}/ (Product Detail)

> **Why after the list:** Detail view is simple once the model and serializer exist.

**Scope:**

- [x] Replace stub `get()` in `ProductDetailView` with real database lookup
- [x] Return `404` JSON if product not found
- [x] Change URL pattern from `<int:pk>` to `<uuid:pk>` (since we use UUID primary keys)


**Files:** `products/views.py`, `products/urls.py`, `tests/`

---

### Issue 5: Add Filtering to Product Feed (Crop Type, Location)

> **Why separate:** Filtering is additive logic on top of a working list endpoint.

**Scope:**

- [x] Add `django-filter` to `requirements.txt`
- [x] Configure `DEFAULT_FILTER_BACKENDS` in `settings.py` (DjangoFilterBackend, SearchFilter, OrderingFilter)
- [x] Create `products/filters.py` with `ProductFilter` (filter by `crop_type`, `location`, price range)
- [x] Add search support (search by `title`, `description`)
- [x] Add ordering support (by `price_per_unit`, `created_at`)
- [x] Add unit tests for each filter in `tests/`

**Files:** `products/filters.py`, `products/views.py`, `config/settings.py`, `requirements.txt`, `tests/`

---

### Issue 6: Add Image URL Storage (Cloudinary Integration)

> **Why last:** Image upload is an external integration and should be isolated per AGENTS.md Rule 11.

**Scope:**

- [x] Add `cloudinary` and `django-cloudinary-storage` to `requirements.txt`
- [x] Add Cloudinary config keys to `.env` and `settings.py` (using env vars — never commit secrets)
- [x] Create `products/image_service.py` to isolate the Cloudinary upload logic
- [x] Add an `ImageField` or use the existing `image_url` (CharField) depending on approach
- [x] Create or update an endpoint for image upload (e.g., `POST /api/products/{id}/image/`)


**Files:** `products/image_service.py`, `products/models.py`, `products/views.py`, `products/urls.py`, `config/settings.py`, `requirements.txt`, `tests/`

---

## Summary Table

| # | Issue Title                                      | Depends On | Key Files                          |
|---|--------------------------------------------------|------------|------------------------------------|
| 1 | Create Product Model                             | —          | `models.py`, `admin.py`            |
| 2 | POST /api/products/ (Create Listing)             | Issue 1    | `serializers.py`, `views.py`, `services.py` |
| 3 | GET /api/products/ (Feed) + Pagination           | Issue 1    | `views.py`, `settings.py`          |
| 4 | GET /api/products/{id}/ (Detail)                 | Issue 1    | `views.py`, `urls.py`              |
| 5 | Add Filtering (crop, location, price, search)    | Issue 3    | `filters.py`, `views.py`           |
| 6 | Image Upload via Cloudinary                      | Issue 1    | `image_service.py`, `views.py`     |
| 7 | Product Listing Tests (Unit + Integration)       | Issues 1–6 | `tests/`                           |

---

### Issue 7: Product Listing Tests (Unit + Integration)

> **Why last:** All product features are complete, so tests can cover the full flow end-to-end.

**Scope:**

#### Unit Tests
- [x] **Model tests:** Product creation, UUID PK generation, farmer FK constraint, field validations, `is_available` default
- [x] **Serializer tests:** Valid input, missing required fields, invalid data types
- [x] **Permission tests:** Farmer can create, buyer cannot create (403), unauthenticated user rejected (401)
- [x] **Filter tests:** Filter by `crop_type`, `location`, price range; search by `title`/`description`
- [x] **Image service tests:** Mock Cloudinary calls, test invalid file types

#### Integration Tests
- [x] **Full product lifecycle:** Create → List → Detail → Update → Delete
- [x] **Marketplace feed:** Pagination, only `is_available=True` returned, ordering
- [x] **Filtering flow:** Combine multiple filters, verify correct result sets
- [x] **Auth flow:** Token-authenticated farmer creates product, buyer browses feed

**Files:** `tests/test_product_model.py`, `tests/test_product_api.py`, `tests/test_product_filters.py`
