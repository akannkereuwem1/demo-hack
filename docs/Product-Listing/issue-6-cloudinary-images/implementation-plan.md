# Issue 6: Add Image URL Storage (Cloudinary Integration) — Implementation Plan

## Goal
Enable farmers to upload product images bypassing the Postgres store by funneling binary data to Cloudinary directly.

## Changes Made

### `requirements.txt`
- Added `cloudinary==1.44.1`.
- Added `django-cloudinary-storage==0.3.0`.

### `config/settings.py`
- Appended `cloudinary` and `cloudinary_storage` to `INSTALLED_APPS`.
- Integrated `CLOUDINARY_STORAGE` config mapping dynamic OS environment variables `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET`.
- Configured Django's default file storage mechanism using `MediaCloudinaryStorage`.

### `products/image_service.py` (NEW)
- Created isolated API integration following architecture decoupling rules.
- Implements `upload_product_image` consuming an in-memory multipart form blob and returning an updated `Product` referencing the secured remote public URL. Overwrites any previous image logic using `overwrite=True` uniquely on `product_X` IDs.

### `products/views.py`
- Implemented `ProductImageUploadView`:
  - Locked under `IsAuthenticated` and `IsFarmer` roles.
  - Ensures robust ownership tests (HTTP 403 blocks non-owners).
  - Handles bad 400 uploads.

### `products/urls.py`
- Exposes `<uuid:pk>/image/` cleanly appended to standard detail queries.

### `tests/test_image_upload.py` (NEW)
- 5 comprehensive checks validating `200` pass-throughs, `401/403` auth blocking, and `400` payload rejections. Mocks `cloudinary.uploader.upload` preserving network silence and independence.

All 70 tests passed.
