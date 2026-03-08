from rest_framework.views import exception_handler
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom exception handler that standardizes all DRF errors into a
    common JSON structure.
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Standardize the response format
        custom_response_data = {
            'success': False,
            'error': {
                'status_code': response.status_code,
                'message': _get_error_message(response.data),
                'details': response.data
            }
        }
        
        # Log the exception
        logger.warning(f"Handled API Exception: {exc}", exc_info=exc)
        
        response.data = custom_response_data
    else:
        # Catch unhandled exceptions (e.g. 500) and explicitly return JSON
        # instead of allowing Django to return HTML
        logger.error(f"Unhandled API Exception: {exc}", exc_info=exc)
        
        # We must return a Response object to DRF with strict JSON
        custom_response_data = {
            'success': False,
            'error': {
                'status_code': 500,
                'message': "Internal Server Error",
                'details': str(exc) if hasattr(exc, '__str__') else "An unexpected error occurred."
            }
        }
        response = Response(custom_response_data, status=500)

    return response

def _get_error_message(error_data):
    """
    Extract a descriptive error message from DRF's default error data.
    """
    if isinstance(error_data, list) and error_data:
        return str(error_data[0])
    elif isinstance(error_data, dict):
        if 'detail' in error_data:
            return str(error_data['detail'])
        # If it's a validation error with field errors, return a generic message
        return "Validation Error"
    return str(error_data)
