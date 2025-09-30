# lab/models.py
"""
Lab models:
 - LabRequest: created when a clinician orders a test (linked to Consultation and Patient).
 - LabResult: created once the lab performs the test and enters results (one-to-one with request).
The model is intentionally light: side effects (billing creation) are handled by signals.py.
"""
from django.db import models
from django.utils import timezone

# Adjust these imports to match your project's model locations if necessary.
try:
    from patients.models import Patient
except Exception:
    Patient = None

try:
    from consultation.models import Consultation, Investigation  # Investigation may contain test metadata
except Exception:
    Consultation = None
    Investigation = None

# Billing model — your billing app likely exposes a Billing (or Bill) model.
try:
    from billing.models import Billing
except Exception:
    Billing = None


class LabRequest(models.Model):
    """
    Represents a requested laboratory investigation.
    - consultation: original consultation where the test was ordered (optional but recommended)
    - investigation: optional FK to an Investigation master record (from consultation app) to pull price/name
    - test_name: textual fallback for the test name
    - status: workflow status (requested -> sample_collected -> processing -> completed)
    """
    STATUS_REQUESTED = "requested"
    STATUS_SAMPLE = "sample_collected"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_REQUESTED, "Requested"),
        (STATUS_SAMPLE, "Sample Collected"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="lab_requests")
    consultation = models.ForeignKey(Consultation, on_delete=models.SET_NULL, null=True, blank=True, related_name="lab_requests")
    investigation = models.ForeignKey(
        "consultation.Investigation", on_delete=models.SET_NULL, null=True, blank=True, related_name="lab_requests"
    )  # optional FK; string to avoid import issues
    test_name = models.CharField(max_length=255, help_text="Human friendly test name; used if investigation is not linked.")
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_REQUESTED)
    notes = models.TextField(blank=True, default="")
    requested_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-requested_at"]
        verbose_name = "Lab Request"
        verbose_name_plural = "Lab Requests"

    def __str__(self):
        return f"LabRequest({self.id}) {self.test_name} for patient {getattr(self.patient, 'id', 'N/A')}"

    def get_display_name(self):
        if self.investigation:
            return getattr(self.investigation, "name", self.test_name)
        return self.test_name

    def get_price(self):
        """
        Returns the price for this investigation:
        - If an Investigation model exists and has a price/fee field, use it.
        - Otherwise, return a sensible default (you can tune this).
        """
        default_price = 500.00  # fallback — adjust to your local default
        inv = getattr(self, "investigation", None)
        if inv:
            # Common field names to try: price, fee, cost
            for attr in ("price", "fee", "cost"):
                if hasattr(inv, attr):
                    try:
                        return float(getattr(inv, attr) or default_price)
                    except (TypeError, ValueError):
                        pass
        return default_price


class LabResult(models.Model):
    """
    Stores the results for a LabRequest.
    - one-to-one relationship ensures only one result record per request (adjust if multiple result entries needed).
    - file_upload optional for attaching PDF/images.
    """
    lab_request = models.OneToOneField(LabRequest, on_delete=models.CASCADE, related_name="result")
    performed_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="lab_results")
    result_text = models.TextField(help_text="Structured or free-text result summary.")
    result_json = models.JSONField(null=True, blank=True, help_text="Optional structured results (JSON).")
    file_upload = models.FileField(upload_to="lab_results/%Y/%m/%d/", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    verified = models.BooleanField(default=False, help_text="Set true once a senior tech/doctor verifies the result.")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Lab Result"
        verbose_name_plural = "Lab Results"

    def __str__(self):
        return f"Result for LabRequest({self.lab_request_id})"
