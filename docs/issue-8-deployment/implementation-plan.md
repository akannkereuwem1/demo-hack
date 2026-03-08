# Issue #8: Deploy Initial Backend to Heroku

## Goal Description
Prepare the Django backend for production deployment to Heroku. This includes updating the dependencies to have production-grade WSGI and static file servers, securely configuring Django settings via environment variables, and writing the platform-specific configuration command (`Procfile`).

## Proposed Changes
- Added `gunicorn` for WSGI server running.
- Added `whitenoise` for serving static files efficiently.
- Added `dj-database-url` to parse environment database URLs.
- Configured `DATABASES` in `backend/config/settings.py` to use `dj-database-url`.
- Removed Render's specific `ALLOWED_HOSTS` logic in `settings.py`. Relying entirely on the `ALLOWED_HOSTS` environment variable.
- Added `whitenoise.middleware.WhiteNoiseMiddleware` after the security middleware.
- Configured `STATIC_ROOT` and set `STATICFILES_STORAGE` to `whitenoise.storage.CompressedManifestStaticFilesStorage`.
- Created platform-specific configuration script (`Procfile`).
- Removed `render.yaml` and `build.sh`.

### Configuration Files
- `Procfile`
- `Dockerfile`
- `.dockerignore`
- `.python-version`

## Verification Plan
1. **Database:** Verifying the DB config works by checking `dj_database_url` behaves properly on production when `DATABASE_URL` is set via Heroku.
2. **Static files:** The Python buildpack automatically runs `collectstatic`.
3. **App Boot:** `gunicorn config.wsgi:application` starts the application without crashing.
