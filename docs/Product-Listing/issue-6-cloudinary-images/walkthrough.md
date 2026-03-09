# Issue 6: Add Image URL Storage (Cloudinary Integration) — Walkthrough

## Summary
Integrated Cloudinary configuration mapping standard multipart payload images from frontend applications onto decoupled external storage servers. 

## Files Changed

| File | Action | Description |
|---|---|---|
| `requirements.txt` | Modified | Pinned cloudinary packages |
| `backend/config/settings.py` | Modified | Active instantiation of Cloudinary configuration pointing toward OS env mappings. |
| `backend/apps/products/image_service.py` | New | Isolated execution file handling actual external uploads. |
| `backend/apps/products/views.py` | Modified | Linked `ProductImageUploadView`. |
| `backend/apps/products/urls.py` | Modified | Exposed `<uuid:pk>/image/` POST route. |
| `backend/tests/test_image_upload.py` | New | Full-range coverage validating HTTP checks and Cloudinary hook logic (Mocked). |
| `TASK.md` | Modified | Marked Issue 6 complete |

## Architecture

```
POST /api/products/<uuid>/image/ (multipart/form-data)
  →  IsAuthenticated + IsFarmer
    →  Fetch Product & match user ownership (returns 403 on fail)
      →  Check payload for `image` parameter (returns 400 on fail)
        →  image_service.upload_product_image(image_file)
          →  cloudinary.uploader.upload(memory_blob, overwrite=True)
            → Extracts secure url (https://res.cloudinary.com/...)
              → product.image_url = new_url -> .save(update_fields)
                → Endpoint returns ProductSerializer object 200 OK
```

## Test Results

```
Ran 70 tests in 45.101s — OK
```

- **5 new** image upload integration tests.
- **65 existing** tests: no regressions. Filtering/Auth stays entirely intact.
