# Walkthrough: Authentication (Issue #20)

## What Was Built

The full authentication system for the AgroNet mobile backend API was implemented across six sub-issues. All features are verified and passing.

---

## Issue #24 — RBAC Permissions

**File:** `backend/apps/users/permissions.py`

Two custom DRF permission classes were created:
- `IsFarmer` — grants access only if `request.user.role == 'farmer'`
- `IsBuyer` — grants access only if `request.user.role == 'buyer'`

These are now available to any view across the project using standard DRF `permission_classes = [IsFarmer]` syntax.

---

## Issue #25 — Bcrypt & JWT Configuration

**Files:** `config/settings.py`, `requirements.txt`

- `bcrypt==5.0.0` added as a dependency
- `PASSWORD_HASHERS` updated — BCryptSHA256 set as primary hasher
- `AUTH_USER_MODEL = 'users.User'` registered
- `SIMPLE_JWT` configured with HS256 algorithm, 60min access token, 1-day refresh token with rotation

---

## Issue #30 — Custom User Model

**Files:** `apps/users/models.py`, `apps/users/migrations/0001_initial.py`

```python
class User(AbstractBaseUser, PermissionsMixin):
    id        = UUIDField(primary_key=True)
    email     = EmailField(unique=True)
    full_name = CharField()
    role      = CharField(choices=Role.choices)  # farmer | buyer
    is_active = BooleanField(default=True)
    is_staff  = BooleanField(default=False)
```

**Migration note:** The database was dropped and recreated to resolve a migration conflict (`admin.0001_initial` depended on Django's default `auth.User` which had already been applied before the custom model was introduced).

---

## Issue #27 — Authentication Serializers

**File:** `apps/users/serializers.py`

| Serializer | Purpose |
|---|---|
| `UserRegistrationSerializer` | Validates & creates new user with hashed password |
| `UserLoginSerializer` | Validates email+password via `authenticate()`, returns user |
| `UserProfileSerializer` | Read-only serializer for profile responses |

---

## Issue #28 — API Endpoints

**Files:** `apps/users/views.py`, `apps/users/urls.py`

| Endpoint | Method | Auth | Response |
|---|---|---|---|
| `/api/users/register/` | POST | Public | `{ user, tokens: { access, refresh } }` |
| `/api/users/login/` | POST | Public | `{ user, tokens: { access, refresh } }` |
| `/api/users/profile/` | GET | Bearer JWT | `{ id, email, role, full_name, ... }` |

---

## Issue #29 — Tests

**File:** `backend/tests/test_users.py`

```
Ran 19 tests in 18.233s

OK
```

### Test Coverage

| Test Class | Tests | Coverage |
|---|---|---|
| `UserManagerTests` | 7 | Model creation, password hashing, UUIDs, properties |
| `RegisterViewTests` | 5 | Happy path, duplicate email, short password, bad role |
| `LoginViewTests` | 3 | Valid login, bad password, unknown email |
| `ProfileViewTests` | 4 | Auth required, farmer profile, buyer profile, JWT claims |

---

## Verification

```
python manage.py check → System check identified no issues (0 silenced).
python manage.py test tests.test_users → Ran 19 tests in 18.233s → OK
```

All authentication sub-issues complete. ✅
