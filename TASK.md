# TASK.md - Issue #20: Authentication

## Scope and Objectives
The goal of this issue is to implement the MVP Authentication feature for the AgroNet mobile backend API. As specified in `AGENTS.md`, authentication must use JWT, include role-based access control (RBAC) for `farmer` and `buyer` roles, and adhere to strict security guidelines (no plaintext passwords, secrets in environment variables).

## Sub-Issues / Implementation Steps

### 1. Implement Role-Based Access Control (RBAC) Permissions #24 (`apps/users/permissions.py`)
- [ ] Create custom DRF permission class `IsFarmer` to restrict access to farmer-only endpoints.
- [ ] Create custom DRF permission class `IsBuyer` to restrict access to buyer-only endpoints.

### 2. Configure Bcrypt Password Hashing & JWT Configuration #25 (`config/settings.py`)
- [ ] Verify `djangorestframework-simplejwt` is configured correctly.
- [ ] Set `AUTH_USER_MODEL` to point to the new custom user model.
- [ ] Configure JWT token lifetimes and settings.

### 3. Authentication Serializers #27 (`apps/users/serializers.py`)
- [ ] Create `UserRegistrationSerializer` handling input validation, role assignment, and secure password hashing.
- [ ] Create `UserLoginSerializer` (or use SimpleJWT's default) to validate credentials and return JWT tokens.
- [ ] Create `UserProfileSerializer` to serialize user details for the frontend.

### 4. API Endpoints #28 (`apps/users/views.py` & `apps/users/urls.py`)
- [ ] **POST /api/users/register/**: Endpoint for user signup.
- [ ] **POST /api/users/login/**: Endpoint for login, returning the JWT `access` and `refresh` tokens.
- [ ] **GET /api/users/profile/**: Protected endpoint to get the authenticated user's profile.
- [ ] Update `apps/users/urls.py` to route these endpoints.

### 5. Testing #29 (`tests/users/`)
- [ ] Write unit tests for user creation and password hashing.
- [ ] Write integration tests for the registration endpoint.
- [ ] Write integration tests for the login endpoint to ensure proper JWT generation.
- [ ] Write integration tests verifying RBAC permissions (e.g., checking that a token with a `buyer` role cannot access a `farmer` endpoint if applicable).

### 6. Custom User Model & Roles #30 (`apps/users/models.py`)
- [ ] Implement or update a Custom `User` model inheriting from `AbstractBaseUser` and `PermissionsMixin`.
- [ ] Define the `Role` choices (`farmer`, `buyer`).
- [ ] Ensure the model uses a UUID primary key.
- [ ] Add required fields (e.g., `email` as unique identifier, `password`, `role`, `is_active`, `is_staff`).
- [ ] Create the custom `UserManager` to handle user creation and superuser creation.
- [ ] Generate and apply database migrations.

## Deliverables
- [ ] `users/permissions.py` with `IsFarmer` and `IsBuyer` classes.
- [ ] Settings updated for JWT and Custom User Model.
- [ ] `users/serializers.py` containing Auth serializers.
- [ ] `users/views.py` and `users/urls.py` exposing Register, Login, and Profile endpoints.
- [ ] Comprehensive test suite in `tests/users/` passing successfully.
- [ ] Updated `users/models.py` with Custom User Model and Role choices.
- [ ] Database migrations for the new User model.
