# lab/admin.py
from django.contrib import admin
from .models import LabRequest, LabResult

@admin.register(LabRequest)
class LabRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "test_name", "patient", "status", "requested_at")
    list_filter = ("status", "requested_at")
    search_fields = ("test_name", "patient__first_name", "patient__last_name", "notes")


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ("id", "lab_request", "performed_by", "created_at", "verified")
    list_filter = ("verified", "created_at")
    search_fields = ("lab_request__test_name", "performed_by__username")
