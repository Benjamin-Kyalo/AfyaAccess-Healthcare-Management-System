# This file registers the LabRequest and LabResult models with the Django admin site
# so that administrators can manage lab records through the Django admin interface.

from django.contrib import admin
# Import our models
from .models import LabRequest, LabResult  

# Register the LabRequest model with custom configuration
@admin.register(LabRequest)
class LabRequestAdmin(admin.ModelAdmin):
    # Display these fields in the admin list view for LabRequest
    list_display = ("id", "test_name", "patient", "status", "requested_at")
    # Allow filtering in the admin sidebar by status and requested_at fields
    list_filter = ("status", "requested_at")
    # Add a search box in admin; allow searching by test name, patient names, or notes
    search_fields = ("test_name", "patient__first_name", "patient__last_name", "notes")


# Register the LabResult model with custom configuration
@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    # Display these fields in the admin list view for LabResult
    list_display = ("id", "lab_request", "performed_by", "created_at", "verified")
    # Allow filtering in the admin sidebar by verification status and creation date
    list_filter = ("verified", "created_at")
    # Add a search box for looking up results by test name or username of lab staff
    search_fields = ("lab_request__test_name", "performed_by__username")
