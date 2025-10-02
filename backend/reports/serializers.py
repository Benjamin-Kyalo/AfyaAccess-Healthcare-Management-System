from rest_framework import serializers

# Serializer for summary report responses
class SummaryReportSerializer(serializers.Serializer):
    # Number of patients registered today
    patients_today = serializers.IntegerField()
    # Number of consultations done today
    consultations_today = serializers.IntegerField()
    # Number of triage records created today
    triage_today = serializers.IntegerField()
    # Number of lab tests requested
    lab_tests_requested = serializers.IntegerField()
    # Number of lab tests completed
    lab_tests_completed = serializers.IntegerField()
    # Total billing amount (paid + unpaid)
    total_bills = serializers.DecimalField(max_digits=10, decimal_places=2)
    # Total unpaid bills amount
    unpaid_bills = serializers.DecimalField(max_digits=10, decimal_places=2)
