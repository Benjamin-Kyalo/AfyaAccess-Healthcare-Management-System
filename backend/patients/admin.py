from django.contrib import admin
from .models import Patient, PatientStatusHistory

# Register Patient model in the admin panel with a custom configuration
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    # Show these fields in the admin list view
    list_display = ("id", "first_name", "last_name", "status", "created_at")
    # Allow searching patients by first/last name, national ID, or phone
    search_fields = ("first_name", "last_name", "national_id", "phone")

# Register PatientStatusHistory model in the admin panel
@admin.register(PatientStatusHistory)
class PatientStatusHistoryAdmin(admin.ModelAdmin):
    # Show these fields in the admin list view
    list_display = ("patient", "old_status", "new_status", "changed_at", "changed_by")
    # Add filter options in the sidebar for old/new status
    list_filter = ("new_status", "old_status")
    # Allow search by patient’s first or last name
    search_fields = ("patient__first_name", "patient__last_name")
