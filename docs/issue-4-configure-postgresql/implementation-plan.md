# Configure PostgreSQL Database (Issue #4)

Set up PostgreSQL as the primary database for the AgroNet backend, replacing the default SQLite configuration.

## Proposed Changes

### Configuration Layer

#### [MODIFY] backend/requirements.txt
Add `psycopg2-binary` (PostgreSQL adapter) and `python-dotenv` (to load environment variables from `.env` files).

#### [NEW] backend/.env.example
Create a template environment file detailing the necessary configuration variables for the database:
- `DB_ENGINE`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

#### [MODIFY] backend/config/settings.py
- Import and configure `dotenv` to load the variables from `.env`.
- Update the `DATABASES` dictionary to read PostgreSQL connection details from environment variables with a fallback for local development or explicit error throwing if variables are unset.

## Verification Plan

### Manual Verification
1. Running `python manage.py check` to ensure the settings are valid.
2. Confirming that if a `.env` file is populated with valid PostgreSQL credentials, the database connections would succeed (developer tasks).
