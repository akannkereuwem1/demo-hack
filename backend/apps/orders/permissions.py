"""
Order-level permission classes for the AgroNet order management feature.

These are object-level permissions applied after authentication checks.
"""

from rest_framework.permissions import BasePermission


class IsOrderParticipant(BasePermission):
    """
    Grants access if the requesting user is either the buyer or the farmer
    on the order.

    Used on the order detail endpoint so both parties can read the order.
    Requirements: 10.4
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """Return True if the user is the buyer or the farmer of the order."""
        return request.user == obj.buyer or request.user == obj.farmer


class IsOrderFarmer(BasePermission):
    """
    Grants access only if the requesting user is the farmer who owns the order.

    Used on confirm, decline, and complete endpoints.
    Requirements: 10.3
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """Return True if the user is the farmer of the order."""
        return request.user == obj.farmer
