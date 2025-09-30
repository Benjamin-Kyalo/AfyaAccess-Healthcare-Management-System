"""
Utility functions and reference ranges for triage vitals.
"""

# Normal ranges for vitals
VITAL_RANGES = {
    "temperature_c": {"normal": (36.0, 37.5), "unit": "°C"},
    "heart_rate_bpm": {"normal": (60, 100), "unit": "bpm"},
    "respiratory_rate_bpm": {"normal": (12, 20), "unit": "bpm"},
    "systolic_bp": {"normal": (90, 120), "unit": "mmHg"},
    "diastolic_bp": {"normal": (60, 80), "unit": "mmHg"},
    "spo2_percent": {"normal": (95, 100), "unit": "%"},
    "bmi": {"normal": (18.5, 24.9), "unit": "kg/m²"},
}

def analyze_vitals(record):
    """
    Analyze a triage record and return a text summary of abnormal vitals.
    Example: "Low temperature: 35.0°C; Bradycardia: 45 bpm"
    """
    alerts = []

    # Temperature
    temp = record.temperature_c
    if temp < 36: alerts.append(f"Low temperature: {temp}°C")
    elif temp > 38: alerts.append(f"Fever: {temp}°C")

    # Heart rate
    hr = record.heart_rate_bpm
    if hr < 60: alerts.append(f"Bradycardia: {hr} bpm")
    elif hr > 100: alerts.append(f"Tachycardia: {hr} bpm")

    # Respiratory rate
    rr = record.respiratory_rate_bpm
    if rr < 12: alerts.append(f"Bradypnea: {rr} bpm")
    elif rr > 20: alerts.append(f"Tachypnea: {rr} bpm")

    # Blood pressure
    sbp, dbp = record.systolic_bp, record.diastolic_bp
    if sbp < 90 or dbp < 60:
        alerts.append(f"Low BP: {sbp}/{dbp} mmHg")
    elif sbp > 140 or dbp > 90:
        alerts.append(f"High BP: {sbp}/{dbp} mmHg")

    # SpO2
    spo2 = record.spo2_percent
    if spo2 < 90: alerts.append(f"Critically low SpO₂: {spo2}%")
    elif spo2 < 95: alerts.append(f"Low SpO₂: {spo2}%")

    # BMI
    bmi = record.bmi
    if bmi:
        if bmi < 18.5: alerts.append(f"Underweight (BMI {bmi})")
        elif bmi > 24.9: alerts.append(f"Overweight/Obese (BMI {bmi})")

    return "; ".join(alerts) if alerts else "All vitals normal"
