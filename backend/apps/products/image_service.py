import cloudinary.uploader
from rest_framework.exceptions import ValidationError

from .models import Product


def upload_product_image(product: Product, image_file) -> Product:
    """
    Uploads an image payload to Cloudinary directly from memory,
    extracts the secure URL, and attaches it back to the Product instance.

    Args:
        product: The Product instance to attach the image to.
        image_file: The uploaded InMemoryUploadedFile from the request.

    Returns:
        The updated Product object.
    
    Raises:
        ValidationError: If the upload operation fails.
    """
    try:
        # Generate an upload targeting our specific AgroNet folder organization
        upload_result = cloudinary.uploader.upload(
            image_file,
            folder='agronet/products/',
            public_id=f'product_{product.id}',
            overwrite=True
        )

        secure_url = upload_result.get('secure_url')
        
        if not secure_url:
            raise ValidationError("Cloudinary failed to return a valid URL.")

        product.image_url = secure_url
        product.save(update_fields=['image_url'])

        return product

    except Exception as e:
        raise ValidationError(f"Image upload process failed: {str(e)}")
