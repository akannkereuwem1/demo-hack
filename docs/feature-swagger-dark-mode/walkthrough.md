# Walkthrough: Swagger UI Dark Mode

This document details the changes made to enable dark mode for the API documentation.

## 1. Custom Template Creation

Created `backend/templates/swagger_dark.html` which extends the base `drf_spectacular/swagger_ui.html`.

This file contains `<style>` blocks that override the default Swagger UI CSS variables and classes to implement a dark color scheme. It targets:
- Main background and text colors
- Operation blocks (GET, POST, etc.)
- Models and schemas
- Input fields and buttons
- Top bar and navigation

## 2. Django Settings Configuration

Updated `backend/config/settings.py` to register the new templates directory.

```python
TEMPLATES = [
    {
        ...
        'DIRS': [BASE_DIR / 'templates'],  # Added this line
        ...
    },
]
```

## 3. URL Configuration

Updated `backend/config/urls.py` to instruct `SpectacularSwaggerView` to use the new custom template.

```python
path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema', template_name='swagger_dark.html'), name='swagger-ui'),
```

## Verification

1. Start the Django development server: `python manage.py runserver`
2. Navigate to `http://127.0.0.1:8000/api/docs/`
3. Verify that the interface is now displayed with a dark background and light text.
