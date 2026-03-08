from rest_framework import permissions

class IsFarmer(permissions.BasePermission):
    """
    Custom permission to only allow access to farmers.
    """
    def has_permission(self, request, view):
        # We assume the custom User model has a `role` attribute.
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'farmer')

class IsBuyer(permissions.BasePermission):
    """
    Custom permission to only allow access to buyers.
    """
    def has_permission(self, request, view):
        # We assume the custom User model has a `role` attribute.
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'buyer')
