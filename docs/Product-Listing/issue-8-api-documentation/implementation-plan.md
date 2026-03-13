# Implementation Plan - Improve Product API Documentation

The current API documentation for products is relying on auto-detection from DRF, which leads to inaccuracies in the Swagger UI. Specifically, read-only fields appear in request examples, role requirements are undocumented, and the image upload endpoint is missing schema information.

## User Review Required

> [!IMPORTANT]
> These changes only affect the API documentation (Swagger/OpenAPI schema) and do not change the underlying business logic or endpoint behavior.

## Proposed Changes

### Products App Documentation

#### [MODIFY] [views.py](file:///c:/Users/WELCOME/Desktop/workspace/demo-hack-pl/backend/apps/products/views.py)
- Import `extend_schema` and related utilities at the top of the file.
- Apply `@extend_schema` to `ProductListView` to:
    - Explicitly define the POST request body fields.
    - Add a description regarding the `farmer` role requirement.
    - Add summaries for GET and POST methods.
- Apply `@extend_schema` to `ProductImageUploadView`:
    - Define the multipart/form-data request body with the `image` field.
    - Remove the redundant imports from inside the `post` method.

## Verification Plan

### Automated Tests
- I will run the existing product API tests to ensure no regressions were introduced.
- Command: `pytest backend/tests/test_product_api.py` (using the environment at `C:\Users\WELCOME\Desktop\workspace\demo-hack-env\Scripts\activate`)

### Manual Verification
- Access `http://127.0.0.1:8000/api/schema/` to verify the generated OpenAPI JSON.
- Access `http://127.0.0.1:8000/api/docs/` to visually inspect the Swagger UI for:
    - Accurate request body examples for `POST /api/products/`.
    - Presence of the `image-upload` endpoint with the `image` file field.
    - Inclusion of "Farmer role required" in descriptions.
