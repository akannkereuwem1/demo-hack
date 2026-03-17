# Implementation Plan: Swagger UI Dark Mode

## Overview
This feature implements dark mode for the Swagger UI documentation to improve readability and aesthetics. It overrides the default `drf-spectacular` template with custom CSS.

## Components & Changes

| Component | Description | Files |
|-----------|-------------|-------|
| Template | Custom HTML template extending `drf_spectacular/swagger_ui.html` | `backend/templates/swagger_dark.html` |
| Settings | Configure Django to look for templates in `backend/templates` | `backend/config/settings.py` |
| URLs | Configure `SpectacularSwaggerView` to use the custom template | `backend/config/urls.py` |

## Architecture Decisions

### Custom Template vs. Static Files
- Instead of serving a static CSS file (requiring `collectstatic` or complex static file serving in development), we injected CSS directly into a template block.
- This approach is simpler for a backend-focused API project and avoids extra dependencies.

### CSS Strategy
- Used a comprehensive set of CSS overrides targeting specific Swagger UI classes to ensure a consistent dark theme.
- Avoided using `filter: invert()` which can lead to color artifacts.
- Manually styled key elements:
    - Backgrounds `#121212`, `#1e1e1e`
    - Text `#e0e0e0`, `#bbb`
    - Inputs and buttons `#2d2d2d`, `#333`
    - Syntax highlighting `#222`
