from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsFarmer

from .filters import ProductFilter
from .models import Product
from .permissions import IsProductOwnerOrReadOnly
from .serializers import ProductSerializer
from .services import create_product
from .image_service import upload_product_image


@extend_schema_view(
    get=extend_schema(
        summary="List Products",
        description="Fetch a paginated list of available agricultural products."
    ),
    post=extend_schema(
        summary="Create Product",
        description="Create a new produce listing. Restricted to users with the 'farmer' role.",
        request=ProductSerializer,
        responses={201: ProductSerializer}
    )
)
class ProductListView(ListCreateAPIView):
    """
    List available products (paginated) or create a new product.

    - GET:  Returns paginated list of available products.
    - POST: Creates a new product (farmer-only).
    """

    serializer_class = ProductSerializer
    queryset = Product.objects.filter(is_available=True)
    filterset_class = ProductFilter
    search_fields = ['title', 'description', 'crop_type']
    ordering_fields = ['price_per_unit', 'created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        """POST requires farmer role; GET is open to authenticated users."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsFarmer()]
        return [IsAuthenticated()]

    def perform_create(self, serializer: ProductSerializer) -> None:
        """Delegate product creation to the service layer."""
        product = create_product(
            farmer=self.request.user,
            validated_data=serializer.validated_data,
        )
        serializer.instance = product


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a product instance by its UUID.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsProductOwnerOrReadOnly]


class ProductImageUploadView(APIView):
    """
    Upload an image for a specific product.
    Requires Farmer role and ownership of the product.
    """
    permission_classes = [IsAuthenticated, IsFarmer]

    @extend_schema(
        summary="Upload Product Image",
        description="Upload an image for a specific product listing. Restricted to the product owner (farmer).",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'The image file to upload.'
                    }
                },
                'required': ['image']
            }
        },
        responses={200: ProductSerializer}
    )
    def post(self, request, pk):
        # 1. Fetch the product and ensure caller owns it
        product = get_object_or_404(Product, pk=pk)
        if product.farmer != request.user:
            return Response(
                {"error": "You do not have permission to modify this product."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 2. Extract image from request
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {"error": "No image file provided in the request payload."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Process upload using the isolated service
        try:
            updated_product = upload_product_image(product, image_file)
            serializer = ProductSerializer(updated_product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
