# Issue #8: Deploy Initial Backend to Render - Walkthrough

## What Was Accomplished
1. Successfully added the production packages (`gunicorn`, `whitenoise`, `dj-database-url`) to `requirements.txt`.
2. Cleaned up and tightened the backend configuration inside `backend/config/settings.py`, adding `RENDER_EXTERNAL_HOSTNAME` to `ALLOWED_HOSTS`.
3. Scaffolded out configuration logic covering the Render platform.
   - Created a `render.yaml` defining the web service for the backend and a PostgreSQL database.
   - Created a `build.sh` script to install requirements, collect static files, and migrate the database during Render's build cycle.
4. Removed the existing `fly.toml` configuration file to complete the transition.

## Deployment Steps
### For Render:
1. Push the code to a source provider (GitHub/GitLab).
2. Go to the Render dashboard.
3. Click "New" and select "Blueprint" (to deploy using `render.yaml`).
4. Connect the repository to your Render account.
5. Review the resources to be created (a Web Service to run the backend and a Free PostgreSQL Database).
6. Click "Apply".
7. Render will execute the steps defined in `build.sh` and deploy the application.
