import io
from decimal import Decimal
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Product, Unit
from users.models import Role, User


class ProductImageUploadTests(APITestCase):
    """Integration functionality for Image Upload endpoint."""

    def setUp(self) -> None:
        self.farmer = User.objects.create_user(
            email='farmer_upload@test.com',
            password='securepass123',
            role=Role.FARMER,
        )
        self.other_farmer = User.objects.create_user(
            email='other_farmer@test.com',
            password='securepass123',
            role=Role.FARMER,
        )
        self.buyer = User.objects.create_user(
            email='buyer_upload@test.com',
            password='securepass123',
            role=Role.BUYER,
        )

        self.product = Product.objects.create(
            farmer=self.farmer,
            title='Test Upload Product',
            description='Waiting for an image',
            crop_type='Yam',
            quantity=Decimal('20.00'),
            unit=Unit.KG,
            price_per_unit=Decimal('100.00'),
            location='Abuja',
            is_available=True,
        )
        self.url = f'/api/products/{self.product.id}/image/'

    def _auth_header(self, user: User) -> dict:
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

    def _generate_test_image(self) -> SimpleUploadedFile:
        # Generate a tiny dummy image file explicitly
        file = io.BytesIO(b"fake_image_data_here")
        file.name = 'test_image.jpg'
        return SimpleUploadedFile("test_image.jpg", file.read(), content_type="image/jpeg")

    @patch('cloudinary.uploader.upload')
    def test_upload_image_success(self, mock_upload) -> None:
        """A farmer can upload an image for their own product."""
        # Setup mock to return a safe secure_url dictionary
        mock_upload.return_value = {
            'secure_url': 'https://res.cloudinary.com/test_cloud/image/upload/v1/agronet/products/test.jpg'
        }

        image = self._generate_test_image()
        response = self.client.post(
            self.url,
            {'image': image},
            format='multipart',
            **self._auth_header(self.farmer)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['image_url'],
            'https://res.cloudinary.com/test_cloud/image/upload/v1/agronet/products/test.jpg'
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.image_url, response.data['image_url'])
        mock_upload.assert_called_once()  # Verify cloudinary backend was hooked into

    def test_upload_image_unauthorized(self) -> None:
        """Unauthenticated requests are rejected."""
        image = self._generate_test_image()
        response = self.client.post(self.url, {'image': image}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_image_wrong_role(self) -> None:
        """Buyers cannot upload images."""
        image = self._generate_test_image()
        response = self.client.post(
            self.url,
            {'image': image},
            format='multipart',
            **self._auth_header(self.buyer)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_image_not_owner(self) -> None:
        """A farmer cannot upload images for another farmer's product."""
        image = self._generate_test_image()
        response = self.client.post(
            self.url,
            {'image': image},
            format='multipart',
            **self._auth_header(self.other_farmer)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_image_no_file(self) -> None:
        """Payload explicitly missing the 'image' key is handled gracefully."""
        response = self.client.post(
            self.url,
            {},  # Empty payload
            format='multipart',
            **self._auth_header(self.farmer)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
