# Issue #8: Deploy Initial Backend to Render

## Goal Description
Prepare the Django backend for production deployment to Render. This includes updating the dependencies to have production-grade WSGI and static file servers, securely configuring Django settings via environment variables, and writing the platform-specific configuration commands (`render.yaml` and Build Scripts).

## Proposed Changes
- Added `gunicorn` for WSGI server running.
- Added `whitenoise` for serving static files efficiently.
- Added `dj-database-url` to parse environment database URLs.
- Configured `DATABASES` in `backend/config/settings.py` to use `dj-database-url`.
- Added support for `RENDER_EXTERNAL_HOSTNAME` in `ALLOWED_HOSTS`.
- Added `whitenoise.middleware.WhiteNoiseMiddleware` after the security middleware.
- Configured `STATIC_ROOT` and set `STATICFILES_STORAGE` to `whitenoise.storage.CompressedManifestStaticFilesStorage`.
- Created platform-specific configuration scripts (`render.yaml`, `build.sh`).
- Removed `fly.toml`.

### Configuration Files
- `Procfile`
- `Dockerfile`
- `.dockerignore`
- `render.yaml`
- `build.sh`
- `.python-version`

## Verification Plan
1. **Database:** Verifying the DB config works by checking `dj_database_url` behaves properly on production when `DATABASE_URL` is set via Render.
2. **Static files:** `python backend/manage.py collectstatic --noinput` runs successfully in the `build.sh` script during the Render build.
3. **App Boot:** `gunicorn config.wsgi:application` starts the application without crashing.
