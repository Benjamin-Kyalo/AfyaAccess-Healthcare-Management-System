"""
Patient service functions: encapsulate matching & registration logic.
Used by views and other modules to avoid duplication.
"""
from typing import List, Dict
from django.db import transaction
from .models import Patient
from django.contrib.auth import get_user_model
User = get_user_model()

def find_possible_matches(data: Dict) -> List[Patient]:
    """
    Simple matching heuristics:
    - exact national_id match (highest priority)
    - exact phone_number match
    - exact name + dob match
    Returns a list of matching Patient objects (may be empty).
    """
    qs = Patient.objects.none()
    national_id = data.get("national_id")
    phone = data.get("phone_number")
    first = data.get("first_name")
    last = data.get("last_name")
    dob = data.get("dob")

    if national_id:
        qs = qs | Patient.objects.filter(national_id__iexact=national_id)
    if phone:
        qs = qs | Patient.objects.filter(phone_number__iexact=phone)
    if first and dob:
        qs = qs | Patient.objects.filter(first_name__iexact=first, dob=dob)
    if last and dob:
        qs = qs | Patient.objects.filter(last_name__iexact=last, dob=dob)

    # Use distinct to avoid duplicates from unions
    return qs.distinct()

@transaction.atomic
def register_patient(data: Dict, created_by: User = None) -> Dict:
    """
    Register a patient if no close match found.
    Returns dict:
      { "patient": Patient instance, "created": bool, "matches": [Patient,...] }
    If matches exist, returns matches and created=False (caller can decide).
    """
    matches = find_possible_matches(data)
    if matches.exists():
        return {"patient": None, "created": False, "matches": list(matches[:10])}

    # No match -- create a new Patient. Using atomic ensures create + any side-effects atomic.
    patient = Patient.objects.create(
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        gender=data.get("gender"),
        dob=data.get("dob"),
        national_id=data.get("national_id"),
        # nhif_number=data.get("nhif_number"),
        phone_number=data.get("phone_number"),
        address=data.get("address"),
        created_by=created_by,
    )
    return {"patient": patient, "created": True, "matches": []}
