# pharmacy/admin.py

from django.contrib import admin
from .models import Drug, Dispense, DispenseLine, AuditLog


# ---------------------------
# Inline: Dispense Lines
# ---------------------------
class DispenseLineInline(admin.TabularInline):
    """
    Inline for showing all drugs dispensed in a single transaction.
    Appears inside the Dispense admin page.
    """
    model = DispenseLine
    extra = 0  # No empty forms by default
    readonly_fields = ("unit_price_at_dispense",)
    fields = ("prescription_item", "drug", "quantity_dispensed", "unit_price_at_dispense")


# ---------------------------
# Drug Admin
# ---------------------------
@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    """
    Manage drugs in the pharmacy inventory.
    Includes quantity tracking, availability, and pricing.
    """
    list_display = ("name", "strength_or_pack", "quantity", "unit_price", "availability_status")
    list_filter = ("availability_status",)
    search_fields = ("name", "strength_or_pack")
    ordering = ("name",)

    # Automatically update availability when saving
    def save_model(self, request, obj, form, change):
        obj.ensure_availability()
        super().save_model(request, obj, form, change)


# ---------------------------
# Dispense Admin
# ---------------------------
@admin.register(Dispense)
class DispenseAdmin(admin.ModelAdmin):
    """
    Manage dispense records, linking prescriptions to dispensed drugs.
    Inline allows viewing of each line item per dispense.
    """
    list_display = ("id", "prescription", "performed_by", "timestamp")
    list_filter = ("performed_by", "timestamp")
    search_fields = ("prescription__id", "performed_by__username")
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)
    inlines = [DispenseLineInline]

    # Automatically assign the user who recorded the dispense
    def save_model(self, request, obj, form, change):
        if not obj.performed_by:
            obj.performed_by = request.user
        super().save_model(request, obj, form, change)


# ---------------------------
# DispenseLine Admin
# ---------------------------
@admin.register(DispenseLine)
class DispenseLineAdmin(admin.ModelAdmin):
    """
    Manage individual dispense line items across all dispenses.
    Useful for detailed audit and reconciliation.
    """
    list_display = ("dispense", "drug", "quantity_dispensed", "unit_price_at_dispense")
    list_filter = ("drug",)
    search_fields = ("drug__name", "dispense__id")
    readonly_fields = ("unit_price_at_dispense",)
    ordering = ("-dispense__timestamp",)


# ---------------------------
# AuditLog Admin
# ---------------------------
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Track all key actions in the pharmacy for transparency and accountability.
    """
    list_display = ("id", "user", "action", "timestamp")
    list_filter = ("action", "user")
    search_fields = ("user__username", "action")
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)
