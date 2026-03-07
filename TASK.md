# TASK.md - Issue #4: Configure PostgreSQL Database

## Objective
Set up PostgreSQL database configuration for the Django backend.

## Deliverables
1. **Requirements Update**: Add `psycopg2-binary` and `python-dotenv` to `requirements.txt`.
2. **Environment Variables Config**: Create `backend/.env.example` to define required database credentials (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT).
3. **Django Settings Update**: Modify `backend/config/settings.py` to:
   - Load `.env` using `python-dotenv`.
   - Configure the `DATABASES` dictionary to use `django.db.backends.postgresql` with environment variables.
4. **Documentation**:
   - `docs/issue-4-configure-postgresql/implementation-plan.md`
   - `docs/issue-4-configure-postgresql/walkthrough.md`

## Next Steps
1. Add dependencies.
2. Setup `.env.example`.
3. Update settings.
4. Complete walkthrough document.
