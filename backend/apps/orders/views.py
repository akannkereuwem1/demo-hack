"""
API views for the Order Management feature.

All business logic is delegated to the service layer (orders/services.py).
Views are responsible only for HTTP handling: input validation, permission
checks, service delegation, and response serialization.
"""

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsBuyer

from .models import Order
from .permissions import IsOrderFarmer, IsOrderParticipant
from .serializers import OrderCreateSerializer, OrderSerializer
from .services import OrderTransitionError, create_order, transition_order


class OrderListView(APIView):
    """
    GET  /api/orders/  — List orders scoped to the requesting user.
    POST /api/orders/  — Create a new order (buyers only).
    """

    def get_permissions(self):
        """Return IsAuthenticated for GET, IsBuyer for POST."""
        if self.request.method == "POST":
            return [IsBuyer()]
        return [IsAuthenticated()]

    def get(self, request: Request) -> Response:
        """
        Return a paginated list of orders for the authenticated user.

        Buyers see only their own orders; farmers see only orders assigned
        to them. Supports optional ?status= query parameter filtering.
        Orders are returned in descending created_at order.
        """
        user = request.user
        queryset = Order.objects.order_by("-created_at")

        if getattr(user, "role", None) == "buyer":
            queryset = queryset.filter(buyer=user)
        elif getattr(user, "role", None) == "farmer":
            queryset = queryset.filter(farmer=user)

        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """
        Create a new order for the authenticated buyer.

        Validates input with OrderCreateSerializer, delegates creation to
        create_order(), and returns the created order with HTTP 201.
        Returns HTTP 400 if the product is unavailable or input is invalid.
        """
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = create_order(
                buyer=request.user,
                product_id=serializer.validated_data["product_id"],
                quantity=serializer.validated_data["quantity"],
                note=serializer.validated_data.get("note", ""),
            )
        except ValidationError as exc:
            message = exc.message if hasattr(exc, "message") else str(exc)
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    # ---------------------------------------------------------------------------
    # Pagination helpers (DRF pagination is configured globally)
    # ---------------------------------------------------------------------------

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            from rest_framework.pagination import PageNumberPagination
            self._paginator = PageNumberPagination()
        return self._paginator

    def paginate_queryset(self, queryset):
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        return self.paginator.get_paginated_response(data)


class OrderDetailView(APIView):
    """
    GET /api/orders/{id}/ — Retrieve a single order by UUID.

    Accessible by the buyer or the farmer on the order (IsOrderParticipant).
    """

    permission_classes = [IsAuthenticated, IsOrderParticipant]

    def get(self, request: Request, pk) -> Response:
        """
        Return the full detail of a single order.

        Returns HTTP 404 if the order does not exist.
        Returns HTTP 403 if the user is neither the buyer nor the farmer.
        """
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(request, order)
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


class OrderConfirmView(APIView):
    """
    PATCH /api/orders/{id}/confirm/ — Farmer confirms a pending order.
    """

    permission_classes = [IsAuthenticated, IsOrderFarmer]

    def patch(self, request: Request, pk) -> Response:
        """
        Transition the order from pending → confirmed.

        Returns HTTP 400 if the transition is invalid.
        Returns HTTP 403 if the user is not the farmer on the order.
        """
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(request, order)

        try:
            updated_order = transition_order(order, target_status="confirmed", actor=request.user)
        except OrderTransitionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        return Response(OrderSerializer(updated_order).data, status=status.HTTP_200_OK)


class OrderDeclineView(APIView):
    """
    PATCH /api/orders/{id}/decline/ — Farmer declines a pending order.
    """

    permission_classes = [IsAuthenticated, IsOrderFarmer]

    def patch(self, request: Request, pk) -> Response:
        """
        Transition the order from pending → declined.

        Returns HTTP 400 if the transition is invalid.
        Returns HTTP 403 if the user is not the farmer on the order.
        """
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(request, order)

        try:
            updated_order = transition_order(order, target_status="declined", actor=request.user)
        except OrderTransitionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        return Response(OrderSerializer(updated_order).data, status=status.HTTP_200_OK)


class OrderCompleteView(APIView):
    """
    PATCH /api/orders/{id}/complete/ — Farmer marks a paid order as completed.
    """

    permission_classes = [IsAuthenticated, IsOrderFarmer]

    def patch(self, request: Request, pk) -> Response:
        """
        Transition the order from paid → completed.

        Returns HTTP 400 if the transition is invalid.
        Returns HTTP 403 if the user is not the farmer on the order.
        """
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(request, order)

        try:
            updated_order = transition_order(order, target_status="completed", actor=request.user)
        except OrderTransitionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        return Response(OrderSerializer(updated_order).data, status=status.HTTP_200_OK)
