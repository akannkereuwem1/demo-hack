# Issue #8: Deploy Initial Backend to Railway/Fly.io - Walkthrough

## What Was Accomplished
1. Successfully added the production packages (`gunicorn`, `whitenoise`, `dj-database-url`) to `requirements.txt`.
2. Cleaned up and tightened the backend configuration inside `backend/config/settings.py`.
3. Scaffolded out configuration logic covering two standard platform-as-a-service providers.
   - For **Railway**: created a `Procfile` mapping the `web` and `release` commands alongside a `.python-version`.
   - For **Fly.io**: created a standard multi-stage caching `Dockerfile`, `fly.toml`, and `.dockerignore`.

## Deployment Steps
### For Railway:
1. Connect your GitHub repository to a new Railway project.
2. Railway will automatically detect the `Procfile` and python environment.
3. Define your environment variables in the Railway dashboard (`DATABASE_URL`, `DJANGO_SECRET_KEY`, `DEBUG=False`).
4. Railway will build from source using the generated Procfile and run database migrations automatically.

### For Fly.io:
1. Install `flyctl`.
2. Login to fly: `fly auth login`.
3. Launch the app `fly launch` inside the root workspace (this reads from the `fly.toml`).
4. Set secrets: `fly secrets set DJANGO_SECRET_KEY=... DATABASE_URL=...`
5. Deploy: `fly deploy`.
