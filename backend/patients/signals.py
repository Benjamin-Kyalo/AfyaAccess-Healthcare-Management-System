from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.apps import apps
from .models import Patient, PatientStatusHistory

# keep a snapshot of old status before saving
@receiver(pre_save, sender=Patient)
def patient_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Patient.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except Patient.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Patient)
def patient_post_save(sender, instance, created, **kwargs):
    """
    - On creation: if initial status is 'registered', we update to 'sent_to_billing' (one extra save).
    - On any save: if status changed, create a PatientStatusHistory record.
    """
    old = getattr(instance, "_old_status", None)

    # 1) If patient was just created and still 'registered', flip to 'sent_to_billing'.
    if created and instance.status == "registered":
        instance.status = "sent_to_billing"
        # calling save() will trigger pre_save/post_save again; the second save will create the history entry
        instance.save()
        return

    # 2) Create history when status changed
    if old != instance.status:
        PatientStatusHistory.objects.create(
            patient=instance,
            old_status=old,
            new_status=instance.status,
            # changed_by remains null here; you may populate changed_by in views if needed
        )


# Billing -> update patient status when invoice is paid (triggered on billing model post_save)
@receiver(post_save)
def generic_post_save(sender, instance, **kwargs):
    """
    This generic receiver checks the sender against the Billing model at runtime,
    so we avoid circular import issues during app loading.
    """
    Billing = apps.get_model("billing", "Billing")
    if sender is not Billing:
        return

    # now instance is a Billing
    try:
        patient = instance.patient
    except Exception:
        patient = None

    if patient and instance.is_paid:
        # only update if different
        if patient.status != "ready_for_doctor":
            patient.status = "ready_for_doctor"
            patient.save()
