from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.apps import apps
from .models import Patient, PatientStatusHistory

# Before saving patient: capture old status for comparison
@receiver(pre_save, sender=Patient)
def patient_pre_save(sender, instance, **kwargs):
    if instance.pk:  # if updating existing patient
        try:
            old = Patient.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except Patient.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


# After saving patient: check for status updates
@receiver(post_save, sender=Patient)
def patient_post_save(sender, instance, created, **kwargs):
    """
    - On creation: if status is 'registered', flip to 'sent_to_billing'.
    - On update: if status changed, log it in PatientStatusHistory.
    """
    old = getattr(instance, "_old_status", None)

    # If new patient was registered, move to "sent_to_billing"
    if created and instance.status == "registered":
        instance.status = "sent_to_billing"
        instance.save()  # triggers another post_save
        return

    # If status changed, create history record
    if old != instance.status:
        PatientStatusHistory.objects.create(
            patient=instance,
            old_status=old,
            new_status=instance.status,
            # changed_by can be filled in views if needed
        )


# Listen to Billing model saves to update patient status
@receiver(post_save)
def generic_post_save(sender, instance, **kwargs):
    """
    Dynamically check if the saved model is Billing (avoids circular import).
    If a bill is paid, update patient status to 'ready_for_doctor'.
    """
    Billing = apps.get_model("billing", "Billing")
    if sender is not Billing:
        return

    patient = getattr(instance, "patient", None)

    # If bill is paid, move patient to doctor queue
    if patient and instance.is_paid:
        if patient.status != "ready_for_doctor":
            patient.status = "ready_for_doctor"
            patient.save()
