# Lab models:
#  - LabRequest: created when a clinician orders a test (linked to Consultation and Patient).
#  - LabResult: created once the lab performs the test and enters results.
# billing creation are handled in signals.py.

# Django ORM base classes
from django.db import models                
# timezone helper for timestamps
from django.utils import timezone           

# Try to import Patient model; if not available keep Patient=None to avoid import errors
try:
    from patients.models import Patient
except Exception:
    Patient = None

# Try to import Consultation and Investigation; avoid hard crash if consultation app missing
try:
    from consultation.models import Consultation, Investigation  # Investigation may hold test metadata
except Exception:
    Consultation = None
    Investigation = None

# Try to import Billing model to allow billing lookups; fallback to None if billing app missing
try:
    from billing.models import Billing
except Exception:
    Billing = None


class LabRequest(models.Model):
    """
    Model representing an ordered lab investigation.
    - consultation: optional link to the originating consultation
    - investigation: optional FK to master Investigation (if used)
    - test_name: fallback textual name if no Investigation is linked
    - status: workflow state for the lab request
    """
    # status constants for request lifecycle
    STATUS_REQUESTED = "requested"
    STATUS_SAMPLE = "sample_collected"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"

    # tuple of choices exposed to admin/UI
    STATUS_CHOICES = [
        (STATUS_REQUESTED, "Requested"),
        (STATUS_SAMPLE, "Sample Collected"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
    ]

    # link to the patient who the test is for
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="lab_requests"
    )

    # optional link to the consultation that triggered the request
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lab_requests"
    )

    # optional foreign key to Investigation (string used to avoid import-time circular refs)
    investigation = models.ForeignKey(
        "consultation.Investigation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lab_requests"
    )

    # human readable test name (used when investigation is absent or as fallback)
    test_name = models.CharField(max_length=255, help_text="Human friendly test name; used if investigation is not linked.")

    # workflow status field with default
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_REQUESTED)

    # free-text notes for additional instructions or sample details
    notes = models.TextField(blank=True, default="")

    # timestamp of when the request was created
    requested_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-requested_at"]              # newest requests first by default
        verbose_name = "Lab Request"
        verbose_name_plural = "Lab Requests"

    def __str__(self):
        # Simple readable representation for admin/debugging
        return f"LabRequest({self.id}) {self.test_name} for patient {getattr(self.patient, 'id', 'N/A')}"

    def get_display_name(self):
        # Prefer linked investigation name if available, otherwise use test_name
        if self.investigation:
            return getattr(self.investigation, "name", self.test_name)
        return self.test_name

    def get_price(self):
        """
        Determine the price for this lab request.
        - If an Investigation is linked and has price/fee/cost attribute, use that.
        - Otherwise return a sensible default (tune as needed).
        """
        default_price = 500.00  # fallback value; consider using Decimal for money
        inv = getattr(self, "investigation", None)
        if inv:
            # try common price attribute names
            for attr in ("price", "fee", "cost"):
                if hasattr(inv, attr):
                    try:
                        return float(getattr(inv, attr) or default_price)
                    except (TypeError, ValueError):
                        # if attribute exists but cannot be parsed to float, ignore and continue
                        pass
        return default_price


class LabResult(models.Model):
    """
    Stores results for a LabRequest.
    - OneToOne ensures one result per request (change if you need multiple result entries).
    - file_upload can be used to attach PDFs, images, etc.
    """
    # Link result to its request (one-to-one)
    lab_request = models.OneToOneField(LabRequest, on_delete=models.CASCADE, related_name="result")

    # Link to the user who performed the test; string used if custom user model lives in users app
    performed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lab_results"
    )

    # Free-text summary of results
    result_text = models.TextField(help_text="Structured or free-text result summary.")

    # Optional structured JSON results (e.g., numeric values keyed by analyte)
    result_json = models.JSONField(null=True, blank=True, help_text="Optional structured results (JSON).")

    # File upload for attachments (PDF, image)
    file_upload = models.FileField(upload_to="lab_results/%Y/%m/%d/", null=True, blank=True)

    # When the result record was created
    created_at = models.DateTimeField(default=timezone.now)

    # Whether a senior tech/doctor has verified the result
    verified = models.BooleanField(default=False, help_text="Set true once a senior tech/doctor verifies the result.")

    class Meta:
        ordering = ["-created_at"]                # newest results first
        verbose_name = "Lab Result"
        verbose_name_plural = "Lab Results"

    def __str__(self):
        # Human-friendly string representation
        return f"Result for LabRequest({self.lab_request_id})"
