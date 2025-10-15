from rest_framework.permissions import BasePermission

# Help to check if user role is in allowed list
def _user_has_role(user, allowed_roles):
    role = getattr(user, "role", None)  # Try to get role attribute from user
    if role:
        return str(role).lower() in {r.lower() for r in allowed_roles}
    # Fallback: allow staff/superuser
    return user.is_staff or user.is_superuser


# Permission: only doctors can create LabRequests
class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return _user_has_role(user, {"doctor", "physician", "clinician", "admin"})


# Permission: lab techs/admin can write; others can only read
class IsLabTechOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # Allow safe methods for everyone
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        # Allow write only for lab staff/admin
        return _user_has_role(user, {"lab", "lab_technician", "lab_tech", "lab_officer", "admin"})
