from rest_framework import permissions


class IsProductOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow farmers to edit their own products.
    Assumes the model instance has an `farmer` attribute.
    """
    message = "You must be the farmer who listed this product to modify it."

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the product.
        return obj.farmer == request.user
