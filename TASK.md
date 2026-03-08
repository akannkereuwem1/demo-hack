# TASK.md - Issue #18: Refactoring to Mobile Backend API Standard

## Current State Analysis
The project currently has `djangorestframework` installed and added to `INSTALLED_APPS`, and a custom exception handler is configured. However, it still lacks the core configurations and structure required for a strict mobile backend API as specified in `AGENTS.md`.

**Does it need refactoring?** Yes. While you are on the right path by including DRF, the project is missing JWT authentication setup, strict JSON rendering, base API routing, and app-level API scaffolding. 

## Planned Refactoring Steps

### 1. Dependency Updates (`requirements.txt`)
- [ ] Add `djangorestframework-simplejwt` for JWT authentication.
- [ ] Add `django-cors-headers` for cross-origin requests (useful for local dev/testing).
- [ ] Add `drf-spectacular` for OpenAPI schema generation (highly recommended to help the mobile team auto-generate API clients).

### 2. Project Configuration (`backend/config/settings.py`)
- [ ] Update `REST_FRAMEWORK` default settings:
  - `DEFAULT_AUTHENTICATION_CLASSES`: Use `JWTAuthentication`.
  - `DEFAULT_PERMISSION_CLASSES`: Set to `IsAuthenticated` so endpoints are secure by default.
  - `DEFAULT_RENDERER_CLASSES`: Enforce `JSONRenderer` only (removes browsable API in production to ensure strict JSON).
  - `DEFAULT_PAGINATION_CLASS`: Set up standard pagination for list endpoints.
- [ ] Configure `SIMPLE_JWT` settings (e.g., token lifetimes).
- [ ] Add and configure `corsheaders` middleware.

### 3. Core Routing (`backend/config/urls.py`)
- [ ] Set up base `api/` routing layout pointing to app-specific URL configurations.
- [ ] Add JWT token endpoints: `api/auth/token/` and `api/auth/token/refresh/`.
- [ ] Ensure no regular Django views exist that return HTML (except `admin/`).

### 4. App-Level Standardization & Scaffolding
- [ ] Ensure each app (`users`, `products`, `orders`, `payments`, `ai`) has a `serializers.py` file.
- [ ] Refactor apps to use DRF `APIView`, `generics`, or `ViewSet` instead of standard Django functional/class-based views.
- [ ] Set up empty/base API endpoints for the MVP features outlined in `AGENTS.md` (e.g., standardizing `GET /api/products`, `POST /api/orders`, etc.).

### 5. Error Handling Standardization (`backend/utils/exceptions.py`)
- [ ] Verify or update `custom_exception_handler` to ensure all errors (400, 401, 403, 404, 500) are returned in a predictable, consistent JSON structure that the mobile frontend can easily parse.

## Deliverables
- [x] Requirements updated with JWT and CORS packages (`requirements.txt`).
- [x] DRF strictly configured for JSON and JWT auth (`config/settings.py`).
- [x] Root API URLs setup (`config/urls.py`).
- [x] `serializers.py` added/updated for all apps (`users`, `products`, `orders`, `payments`, `ai`).
- [x] Refactored mobile-friendly API views replacing standard Django views.
- [x] All error responses strictly returning JSON layout (`utils/exceptions.py`).

---

**Note:** The mobile backend API refactoring implementation for Issue #18 is fully complete.
