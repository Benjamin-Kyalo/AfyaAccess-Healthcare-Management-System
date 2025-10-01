from rest_framework import serializers

class SummaryReportSerializer(serializers.Serializer):
    patients_today = serializers.IntegerField()
    consultations_today = serializers.IntegerField()
    triage_today = serializers.IntegerField()
    lab_tests_requested = serializers.IntegerField()
    lab_tests_completed = serializers.IntegerField()
    total_bills = serializers.DecimalField(max_digits=10, decimal_places=2)
    unpaid_bills = serializers.DecimalField(max_digits=10, decimal_places=2)
