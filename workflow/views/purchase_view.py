from django.views.generic import TemplateView
from django.http import JsonResponse
from workflow.models import Purchase


class PurchaseEntryView(TemplateView):
    template_name = "purchases/purchase_entry.html"

    def get(self, request, job_id=None, *args, **kwargs):
        purchases = Purchase.objects.filter(job_id=job_id).values()
        return JsonResponse({
            "success": True, 
            "purchases": list(purchases)
            }, status=200)
