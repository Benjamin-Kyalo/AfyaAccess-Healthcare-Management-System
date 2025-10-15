from rest_framework.permissions import BasePermission

class IsReceptionOrAdmin(BasePermission):
    """
    Allow create/list for users in Reception group or is_staff.
    Other actions controlled at viewset/object-level (authentication required).
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        # Group-based: user must belong to 'Reception' group to create/list
        return view.action in ("create", "list") and user.groups.filter(name="Reception").exists()
