# Issue #8: Deploy Initial Backend to Heroku - Walkthrough

## What Was Accomplished
1. Successfully added the production packages (`gunicorn`, `whitenoise`, `dj-database-url`) to `requirements.txt`.
2. Cleaned up and tightened the backend configuration inside `backend/config/settings.py`, relying on the environment for `ALLOWED_HOSTS`.
3. Scaffolded out configuration logic covering the Heroku platform.
   - Created a `Procfile` defining the web service for the backend and a release process for migrations.
   - Ensured `.python-version` is present to dictate the correct Python runtime for Heroku.
4. Removed the existing Render configuration files (`render.yaml`, `build.sh`) to complete the transition.

## Deployment Steps
### For Heroku:
1. Ensure you have the Heroku CLI installed and are logged in.
2. Navigate to your project directory.
3. Create a new Heroku app:
   ```bash
   heroku create agronet-backend
   ```
4. Add the PostgreSQL add-on and specify your preferred plan:
   ```bash
   heroku addons:create heroku-postgresql:essential-0
   ```
5. Configure environment variables like `DJANGO_SECRET_KEY` and `ALLOWED_HOSTS`:
   ```bash
   heroku config:set DJANGO_SECRET_KEY="your-secure-key"
   heroku config:set ALLOWED_HOSTS="agronet-backend.herokuapp.com"
   ```
6. Deploy the code to Heroku:
   ```bash
   git push heroku main
   ```
7. Heroku will execute the Python buildpack, automatically run `collectstatic`, and the `release` phase in the `Procfile` will apply migrations.
