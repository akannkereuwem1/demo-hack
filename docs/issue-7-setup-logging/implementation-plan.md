# Issue 7: Setup logging and error handling

## Goal Description
Implement standardize testing and logging functionality within Django and DRF for the AgroNet backend API.

## Completed Changes
### Backend Utils
- Added `backend/utils/exceptions.py`. Contains `custom_exception_handler` to standardize all DRF exceptions into a uniform JSON response format: `{"success": false, "error": {"status_code": x, "message": y, "details": z}}`.
- Contains `_get_error_message` utility string builder.

### Backend Config
- Updated `backend/config/settings.py`. Includes Python `LOGGING` configuring generic formatters alongside separate console/logfile handlers.
- Sets standard warning filtering (`django_warnings.log`), sets default system logs to INFO and limits raw error bubbling for better security context.
- Injects native generic error configuration into `REST_FRAMEWORK` parameters automatically replacing old exception flow.

### Backend Tests
- Added `backend/tests/test_exceptions.py` checking validation formatting logic, standard DRF internal exception tracking and handling validation errors reliably. 
- Integrated a generic config verification test guaranteeing settings accurately load configuration patterns.

## Next Steps
- Implement broader exception middleware capturing edge cases directly resulting from views.
