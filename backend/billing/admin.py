from django.contrib import admin
from .models import Billing, Payment


# ---------------------------
# Inline admin for Payments
# ---------------------------
class PaymentInline(admin.TabularInline):
    """
    Allows Payments to be managed directly from the Billing page.
    Displays key fields only for clarity.
    """
    model = Payment
    extra = 0  # don't show empty forms by default
    readonly_fields = ("created_at",)  # creation time should not be edited
    fields = ("amount", "payment_method", "reference_number", "created_by", "created_at")


# ---------------------------
# Billing Admin
# ---------------------------
@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    """
    Customize how Billing entries appear in the Django admin.
    Includes key financial and relational info for quick access.
    """
    list_display = (
        "invoice_number",
        "patient_name",
        "service",
        "amount",
        "currency",
        "status",
        "is_paid",
        "charged_by_name",
        "created_at",
    )
    list_filter = ("status", "service", "currency", "charged_by")
    search_fields = ("invoice_number", "patient_name", "charged_by_name", "report_reference")
    readonly_fields = ("invoice_number", "created_at", "updated_at", "charged_by_name", "patient_name")
    ordering = ("-created_at",)

    # Attach inline payments for one-stop management
    inlines = [PaymentInline]

    # Automatically set the charged_by user when adding a new Billing record
    def save_model(self, request, obj, form, change):
        if not obj.charged_by:
            obj.charged_by = request.user
            obj.charged_by_name = request.user.get_full_name() or request.user.username
        super().save_model(request, obj, form, change)


# ---------------------------
# Payment Admin
# ---------------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Customize how Payments appear in the admin interface.
    Focuses on audit trail and quick lookup.
    """
    list_display = (
        "id",
        "billing",
        "amount",
        "payment_method",
        "reference_number",
        "created_by",
        "created_at",
    )
    list_filter = ("payment_method", "created_by")
    search_fields = ("reference_number", "billing__invoice_number", "billing__patient_name")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    # Auto-assign created_by to the logged-in user
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
