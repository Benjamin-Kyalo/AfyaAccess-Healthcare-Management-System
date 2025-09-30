from django.contrib import admin
from .models import TriageRecord

@admin.register(TriageRecord)
class TriageRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "attended_by", "created_at", "temperature_c", "heart_rate_bpm")
    search_fields = ("patient__first_name", "patient__last_name", "attended_by__username")
    list_filter = ["created_at"]
