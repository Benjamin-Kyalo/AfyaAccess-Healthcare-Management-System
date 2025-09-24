from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def health_check(request):
    """Simple health check - returns JSON {"status": "ok"}"""
    return JsonResponse({"status": "ok"})