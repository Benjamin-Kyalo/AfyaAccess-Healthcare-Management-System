# lab/permissions.py
"""
Custom permissions:
 - Only doctors can create LabRequests (they order tests).
 - Lab technicians / lab roles (or staff) can add LabResults but results are further guarded by billing.
Adjust role checks to match your User model's 'role' field if present.
"""
from rest_framework.permissions import BasePermission


def _user_has_role(user, allowed_roles):
    role = getattr(user, "role", None)
    if role:
        return str(role).lower() in {r.lower() for r in allowed_roles}
    # fallback to staff/superuser
    return user.is_staff or user.is_superuser


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return _user_has_role(user, {"doctor", "physician", "clinician", "admin"})


class IsLabTechOrReadOnly(BasePermission):
    """
    Allow POST/PUT/DELETE only for lab techs/admin; allow GET for authenticated users.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        # For writing actions, require lab role
        return _user_has_role(user, {"lab", "lab_technician", "lab_tech", "lab_officer", "admin"})
