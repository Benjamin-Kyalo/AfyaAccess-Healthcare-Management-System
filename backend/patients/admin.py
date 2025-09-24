from django.contrib import admin
from .models import Patient, PatientStatusHistory

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id","first_name","last_name","status","registered_at")
    search_fields = ("first_name","last_name","national_id","phone")

@admin.register(PatientStatusHistory)
class PatientStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("patient","old_status","new_status","changed_by","timestamp")
    list_filter = ("new_status","old_status")
    search_fields = ("patient__first_name","patient__last_name")
