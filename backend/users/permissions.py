"""
Custom permission:
- list/create/delete => staff (is_staff) only
- retrieve => authenticated
- update/partial_update => admin OR the user themselves
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrSelf(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Actions that require admin (list/create/destroy mapped to view.action)
        action = getattr(view, "action", None)
        if action in ("list", "create", "destroy"):
            return user.is_staff
        # For other actions allow to proceed to object-level checks.
        return True

    def has_object_permission(self, request, view, obj):
        # Safe methods (GET, HEAD, OPTIONS) are allowed for authenticated users.
        if request.method in SAFE_METHODS:
            return True
        # Mutations allowed for admin or the owner (self).
        return request.user.is_staff or obj == request.user
