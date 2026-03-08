# Implementation Plan: Authentication (Issue #20)

## Overview
Issue #20 covers the full MVP Authentication feature for the AgroNet mobile backend API. It was broken into six sub-issues and implemented iteratively.

## Sub-Issues & Scope

| Issue | Title | Files |
|-------|-------|-------|
| #24 | RBAC Permissions | `apps/users/permissions.py` |
| #25 | Bcrypt + JWT Configuration | `config/settings.py`, `requirements.txt` |
| #27 | Authentication Serializers | `apps/users/serializers.py` |
| #28 | API Endpoints | `apps/users/views.py`, `apps/users/urls.py` |
| #29 | Testing | `tests/test_users.py` |
| #30 | Custom User Model | `apps/users/models.py`, migrations |

## Architecture Decisions

### Custom User Model (Issue #30)
- Inherits from `AbstractBaseUser` + `PermissionsMixin`
- Uses `email` as `USERNAME_FIELD` (not username)
- UUID primary key for all users
- `role` field with `TextChoices`: `farmer` / `buyer`
- Custom `UserManager` with `create_user` and `create_superuser`

### Password Hashing (Issue #25)
- `bcrypt==5.0.0` installed to the shared `demo-hack-env` virtual environment
- `PASSWORD_HASHERS` in `settings.py` sets `BCryptSHA256PasswordHasher` as the primary hasher
- Django's `set_password()` in `UserManager.create_user` handles hashing automatically

### JWT Configuration (Issue #25)
- `AUTH_USER_MODEL = 'users.User'` registered in settings
- `SIMPLE_JWT` configured with:
  - 60-minute `ACCESS_TOKEN_LIFETIME`
  - 1-day `REFRESH_TOKEN_LIFETIME` with token rotation
  - `HS256` algorithm, `Bearer` header type
  - `user_id` claim keyed to the UUID `id` field

### RBAC Permissions (Issue #24)
- `IsFarmer`: allows only authenticated users with `role == 'farmer'`
- `IsBuyer`: allows only authenticated users with `role == 'buyer'`
- Both classes use `getattr(user, 'role', None)` for safe access

### API Endpoints (Issue #28)
All endpoints under `/api/users/`:

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| POST | `/api/users/register/` | AllowAny | Register new farmer or buyer |
| POST | `/api/users/login/` | AllowAny | Login, returns JWT tokens |
| GET | `/api/users/profile/` | IsAuthenticated | Get authenticated user's profile |

### Serializers (Issue #27)
- `UserRegistrationSerializer`: validates email, password (min 8 chars), role; calls `create_user` on save
- `UserLoginSerializer`: validates credentials via `authenticate()`; attaches user to `validated_data`
- `UserProfileSerializer`: read-only output serializer for user profile responses

## Migration Notes
- `python manage.py makemigrations users` → created `users/migrations/0001_initial.py`
- Database (`agronet_db`) was dropped and recreated to resolve `admin.0001_initial` dependency conflict caused by switching to a custom user model after initial migrations had been applied
- All migrations applied successfully on the fresh database

## Files Changed
- `backend/apps/users/models.py` — full custom User model
- `backend/apps/users/permissions.py` — IsFarmer, IsBuyer
- `backend/apps/users/serializers.py` — Register, Login, Profile serializers
- `backend/apps/users/views.py` — RegisterView, LoginView, ProfileView
- `backend/apps/users/urls.py` — URL routing
- `backend/apps/users/migrations/0001_initial.py` — DB migration
- `backend/config/settings.py` — AUTH_USER_MODEL, PASSWORD_HASHERS, SIMPLE_JWT
- `backend/requirements.txt` — added bcrypt==5.0.0
- `backend/tests/test_users.py` — full test suite
