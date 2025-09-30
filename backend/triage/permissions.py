from rest_framework import permissions

class IsClinicianOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Clinicians (staff) can create/update/delete triage records
    - Everyone else can only view (GET requests).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
