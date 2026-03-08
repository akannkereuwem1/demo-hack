from django.test import TestCase
from rest_framework.exceptions import ValidationError, APIException
from utils.exceptions import custom_exception_handler, _get_error_message
from unittest.mock import patch
import logging

class ExceptionHandlerTests(TestCase):
    def test_validation_error_formatting(self):
        """Test how the handler formats a standard DRF ValidationError"""
        exc = ValidationError({"field": ["This field is required."]})
        context = {"view": None, "request": None}
        
        response = custom_exception_handler(exc, context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"]["status_code"], 400)
        # Should extract a message. The detail dict is passed.
        self.assertEqual(response.data["error"]["message"], "Validation Error")
        
    def test_generic_api_exception(self):
        """Test formatting of a standard APIException"""
        exc = APIException("Something went wrong.")
        context = {"view": None, "request": None}
        
        response = custom_exception_handler(exc, context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data["error"]["message"], "Something went wrong.")

    @patch('utils.exceptions.logger.error')
    def test_unhandled_exception_logging(self, mock_logger_error):
        """Test that unhandled standard python exceptions are logged and return 500 JSON"""
        exc = ValueError("A nasty internal error")
        context = {"view": None, "request": None}
        
        response = custom_exception_handler(exc, context)
        
        # When exception_handler returns None, custom handler should explicitly return a 500 Response
        # and it should log an error.
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data["error"]["message"], "Internal Server Error")
        mock_logger_error.assert_called_once()
        args, kwargs = mock_logger_error.call_args
        self.assertIn("Unhandled API Exception", args[0])

    def test_get_error_message_logic(self):
        """Test the internal method for extracting user-friendly messages"""
        self.assertEqual(_get_error_message({"detail": "Not found"}), "Not found")
        self.assertEqual(_get_error_message(["Error 1", "Error 2"]), "Error 1")
        self.assertEqual(_get_error_message("Simple string"), "Simple string")

class LoggingConfigTests(TestCase):
    def test_logging_is_configured(self):
        """Verify the logging configuration has been loaded correctly"""
        from django.conf import settings
        self.assertIn('LOGGING', dir(settings))
        
        # Check that we configured the console and file handlers
        handlers = settings.LOGGING.get('handlers', {})
        self.assertIn('console', handlers)
        self.assertIn('file', handlers)
        
        # Check our specific loggers
        loggers = settings.LOGGING.get('loggers', {})
        self.assertIn('django', loggers)
        self.assertIn('utils', loggers)
