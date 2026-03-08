# Issue #18: Mobile Backend API Refactoring - Implementation Plan

## Objective
Convert the current Django configuration into a strict Django REST Framework (DRF) mobile backend API as directed by `AGENTS.md`.

## Changes Made

### 1. Dependencies added
- `djangorestframework-simplejwt`: For stateless JWT token authentication
- `django-cors-headers`: For frontend cross-origin requests
- `drf-spectacular`: For OpenAPI schema generation (useful for mobile clients)
- `dj-database-url`, `psycopg2-binary`: Database URL parsing and Postgres adapter. 

### 2. Django Settings (`config/settings.py`)
- Removed browsable API renderers, enforcing `JSONRenderer` for standard DRF output.
- Configured default permissions to `IsAuthenticated` to ensure API security by default.
- Added `corsheaders` middleware.
- Configured SimpleJWT token lifetimes.

### 3. Core Routing (`config/urls.py`)
- Included `api/schema/` and `api/docs/` for OpenAPI docs.
- Added `api/auth/token/` and `api/auth/token/refresh/` for JWT token management.
- Wired all isolated apps under the `/api/` path (`/api/users/`, etc).

### 4. App-Level Structuring
- For `users`, `products`, `orders`, `payments`, and `ai`:
  - Created base `serializers.py`.
  - Created placeholder `APIView` classes for each MVP feature in their respective `views.py`.
  - Created `urls.py` files to define standard routing for each application.

### 5. Exception Handling
- Modified `utils/exceptions.py`.
- Enforced a strict JSON format for *all* errors, including `500 Server Errors`, to guarantee the mobile client never tries to parse an HTML exception page.
