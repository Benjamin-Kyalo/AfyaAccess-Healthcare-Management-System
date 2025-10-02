from django.contrib import admin
from .models import TriageRecord

# Register TriageRecord model in Django Admin
@admin.register(TriageRecord)
class TriageRecordAdmin(admin.ModelAdmin):
    # Display key fields in the admin list view
    list_display = ("id", "patient", "attended_by", "created_at", "temperature_c", "heart_rate_bpm")
    # Allow searching by patient name or attending clinician
    search_fields = ("patient__first_name", "patient__last_name", "attended_by__username")
    # Add filters for quick filtering by creation date
    list_filter = ["created_at"]
