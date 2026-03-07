# Walkthrough: Configure PostgreSQL Database (Issue #4)

## Changes Made

1. **Requirements**
   - Added `psycopg2-binary>=2.9.0` for PostgreSQL connectivity.
   - Added `python-dotenv>=1.0.0` for parsing `.env` files.

2. **Environment Template**
   - Created `backend/.env.example` containing typical configuration options (e.g., `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).

3. **Django Settings (`backend/config/settings.py`)**
   - Implemented `dotenv.load_dotenv()` to pull configuration gracefully.
   - Replaced default SQLite configuration in `DATABASES['default']` with `django.db.backends.postgresql`.
   - Setup dictionary mappings for matching environment variable keys with safe defaults (like `127.0.0.1` and `5432`) for unconfigured local developer setups.

## Validation / Testing

- The Python syntax and dictionary modifications for `DATABASES` are safe and PEP8 compliant.
- Developers can now securely use environment configurations without risking commit of database credentials.
