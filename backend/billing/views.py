# billing/views.py
"""
ViewSets for Billing and Payment.

- BillingViewSet: list/create/retrieve/update/destroy plus custom actions:
  - reports: aggregated metrics
  - search: search by patient/invoice
  - add_payment: create a payment for a given bill
  - mark_paid: create payment for outstanding balance
  - cancel: mark bill cancelled
- PaymentViewSet: list/create/retrieve/update/delete payments directly (each action refreshes billing status)
"""

from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters
from django.db.models import Sum

from .models import Billing, Payment
from .serializers import BillingSerializer, PaymentSerializer


class BillingViewSet(viewsets.ModelViewSet):
    """ViewSet for Billing model and related custom actions."""

    queryset = Billing.objects.all().order_by("-created_at")
    serializer_class = BillingSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["invoice_number", "patient_name", "service", "charged_by_name"]
    ordering_fields = ["created_at", "amount"]

    @action(detail=False, methods=["get"])
    def reports(self, request):
        """Return aggregated billing metrics for dashboards."""
        total_paid = Billing.objects.paid_total()
        total_unpaid = Billing.objects.unpaid_total()
        total_partial = Billing.objects.filter(status=Billing.STATUS_PARTIAL).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        total_cancelled = Billing.objects.cancelled_total()
        by_service = list(Billing.objects.total_by_service())

        return Response(
            {
                "total_paid": total_paid,
                "total_unpaid": total_unpaid,
                "total_partial": total_partial,
                "total_cancelled": total_cancelled,
                "by_service": by_service,
            }
        )

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Search bills by patient name/ID or invoice (preserves your earlier helper)."""
        q = request.query_params.get("q", None)
        if q:
            bills = Billing.objects.by_patient_name_or_id(q).order_by("-created_at")
        else:
            bills = Billing.objects.all().order_by("-created_at")
        page = self.paginate_queryset(bills)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(bills, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_payment(self, request, pk=None):
        """
        Add a payment to this billing record.
        POST body: {"amount": 500, "payment_method":"mpesa", "reference_number":"ABC"}
        """
        billing = self.get_object()
        data = request.data or {}
        amount = data.get("amount")
        method = data.get("payment_method", "cash")
        reference = data.get("reference_number", None)

        if amount is None:
            return Response({"detail": "amount is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount_dec = Decimal(str(amount))
        except Exception:
            return Response({"detail": "Invalid amount format"}, status=status.HTTP_400_BAD_REQUEST)
        if amount_dec <= Decimal("0.00"):
            return Response({"detail": "amount must be positive"}, status=status.HTTP_400_BAD_REQUEST)

        payment = billing.create_payment(amount=amount_dec, method=method, reference=reference, user=request.user)
        payment_data = PaymentSerializer(payment, context={"request": request}).data
        billing_data = BillingSerializer(billing, context={"request": request}).data
        return Response({"payment": payment_data, "billing": billing_data}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        """Pay outstanding balance in full (creates Payment entry and updates billing status)."""
        billing = self.get_object()
        balance = billing.calculate_balance()
        if balance <= Decimal("0.00"):
            serializer = BillingSerializer(billing, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        method = request.data.get("payment_method", "manual")
        reference = request.data.get("reference_number", None)
        payment = billing.create_payment(amount=balance, method=method, reference=reference, user=request.user)
        serializer = BillingSerializer(billing, context={"request": request})
        return Response({"payment_id": payment.id, "billing": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a billing record (keeps payments for audit)."""
        billing = self.get_object()
        reason = request.data.get("reason")
        billing.cancel(reason=reason, user=request.user)
        serializer = BillingSerializer(billing, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    CRUD for Payment entries.
    Creating/updating/deleting payments will refresh the linked Billing's status automatically.
    """

    queryset = Payment.objects.all().order_by("-created_at")
    serializer_class = PaymentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["reference_number", "payment_method"]
    ordering_fields = ["created_at", "amount"]

    def create(self, request, *args, **kwargs):
        """
        Ensure created_by is set from request user (audit) and return updated billing in response.
        """
        request_data = request.data.copy()
        if "created_by" not in request_data and hasattr(request, "user"):
            request_data["created_by"] = request.user.pk
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        billing_data = BillingSerializer(payment.billing, context={"request": request}).data
        payment_data = serializer.data
        return Response({"payment": payment_data, "billing": billing_data}, status=status.HTTP_201_CREATED)
