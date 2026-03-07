# TASK: Issue #7 - Setup logging and error handling

## Scope
- Implement a consistent JSON error response format across the Django REST Framework (DRF) API.
- Set up Django logging configuration to capture info, warnings, and errors while ensuring no sensitive data is logged (as per Security Rules).
- Create tests for both error handling output and logging functionality.
- Add project documentation for the issue.

## Checklist

- [x] **1. Create Custom Exception Handler (Utils/Error Handling)**
  - Implement a DRF custom exception handler in `backend/utils/exceptions.py`.
  - Ensure formatting standardizes all API errors (validation, auth, server errors) into a common JSON structure.

- [x] **2. Setup Django Logging (Config)**
  - Update `backend/config/settings.py` (or create `backend/config/logging.py`) to configure Python's `logging` dictionary.
  - Add formatters and handlers (console, and optionally rotated file logs).
  - Configure loggers for `django`, `django.request`, and custom `apps`.
  - Prevent logging of sensitive information.

- [x] **3. Write Tests**
  - Add tests in `backend/tests/` to trigger general exceptions and verify the custom exception handler JSON output.
  - Add tests for logging config pip installlverification.

- [x] **4. Create Deliverables Documentation**
  - Create `docs/issue-7-setup-logging/implementation-plan.md`.
  - Create `docs/issue-7-setup-logging/walkthrough.md`.
  - Update `docs` as required by rule 16 when finished.

## Definition of Done
- Exception handler is active and works for all APIs.
- Logging captures correct levels (INFO/ERROR) without spilling secrets.
- Tests (unit/integration) pass.
- Flake8/PEP8 linting passes.
- Agent stops and waits for next instruction after committing work.
