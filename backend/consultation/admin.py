from django.contrib import admin
from .models import Consultation, Diagnosis, Investigation, Prescription, PrescriptionItem


# ✅ Register Investigation model
@admin.register(Investigation)
class InvestigationAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "availability_status")
    search_fields = ("name",)
    list_filter = ("availability_status",)


# ✅ Register Diagnosis model
@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# ✅ Register Consultation model
@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    # These fields exist in your model — so we can safely show them
    list_display = ("patient_name", "doctor_name", "complaints", "created_at")

    # Allow searching by name or complaint
    search_fields = ("patient_name", "doctor_name", "complaints")

    # Add filters for quick admin navigation
    list_filter = ("created_at",)

    # Optional: make created_at read-only
    readonly_fields = ("created_at",)


# ✅ Register Prescription model
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "consultation", "status", "created_by", "created_at")
    search_fields = ("consultation__patient_name",)
    list_filter = ("status", "created_at")


# ✅ Register PrescriptionItem model
@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = (
        "prescription",
        "drug",
        "quantity_requested",
        "quantity_dispensed",
        "unit",
        "route",
        "frequency",
    )
    search_fields = ("drug__name", "prescription__consultation__patient_name")
