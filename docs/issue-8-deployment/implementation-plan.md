# Issue #8: Deploy Initial Backend to Railway/Fly.io

## Goal Description
Prepare the Django backend for production deployment to PaaS providers like Railway or Fly.io. This includes updating the dependencies to have production-grade WSGI and static file servers, securely configuring Django settings via environment variables, and writing the platform-specific configuration commands.

## Proposed Changes
- Added `gunicorn` for WSGI server running.
- Added `whitenoise` for serving static files efficiently.
- Added `dj-database-url` to parse environment database URLs.
- Configured `DATABASES` in `backend/config/settings.py` to use `dj-database-url`.
- Updated `ALLOWED_HOSTS` to fallback to wildcard `*` if not provided to avoid quick host issues.
- Added `whitenoise.middleware.WhiteNoiseMiddleware` after the security middleware.
- Configured `STATIC_ROOT` and set `STATICFILES_STORAGE` to `whitenoise.storage.CompressedManifestStaticFilesStorage`.
- Created platform-specific configuration scripts (`Procfile`, `Dockerfile`, `fly.toml`, `.dockerignore`, `.python-version`).

### Configuration Files
- `Procfile`
- `Dockerfile`
- `.dockerignore`
- `fly.toml`
- `.python-version`

## Verification Plan
1. **Database:** Verifying the DB config works by checking `dj_database_url` behaves properly on production when `DATABASE_URL` is set.
2. **Static files:** `python manage.py collectstatic --noinput` runs successfully in the generated Dockerfile.
3. **App Boot:** `gunicorn config.wsgi:application` starts the application without crashing.
