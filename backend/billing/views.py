from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Billing
from .serializers import BillingSerializer

# ViewSet for handling billing endpoints
class BillingViewSet(viewsets.ModelViewSet):
    # Return all bills ordered by most recent
    queryset = Billing.objects.all().order_by("-charged_at")
    serializer_class = BillingSerializer

    # Custom endpoint: /billing/reports/
    @action(detail=False, methods=["get"])
    def reports(self, request):
        total_paid = Billing.objects.paid_total()
        total_unpaid = Billing.objects.unpaid_total()
        return Response({
            "total_paid": total_paid,
            "total_unpaid": total_unpaid,
        })

    # Custom endpoint: /billing/search/?q=...
    @action(detail=False, methods=["get"])
    def search(self, request):
        q = request.query_params.get("q", None)
        if q:
            bills = Billing.objects.by_patient_name_or_id(q)
        else:
            bills = Billing.objects.all()
        serializer = self.get_serializer(bills, many=True)
        return Response(serializer.data)
