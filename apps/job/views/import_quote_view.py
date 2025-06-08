"""API endpoint to import quote spreadsheets.

Example usage with ``curl``::

    curl -X POST -F "file=@quote.xlsx" \
         http://localhost:8000/jobs/api/jobs/<job_id>/import-quote/

This will create ``JobPart`` and related entries from the spreadsheet.
"""

from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from apps.job.models import Job
from apps.job.services.quote_import_service import import_quote_from_excel

logger = logging.getLogger(__name__)


class ImportQuoteView(APIView):
    """Handle spreadsheet uploads and create pricing entries."""

    permission_classes = [IsAuthenticated]

    def post(self, request, job_id, *args, **kwargs):
        job = get_object_or_404(Job, id=job_id)

        file = request.FILES.get("file")
        if not file:
            return Response({"error": "File is required"}, status=status.HTTP_400_BAD_REQUEST)

        job_pricing_id = request.data.get("job_pricing_id")

        try:
            job_pricing, parts_created, material_cost, adjustment_cost = import_quote_from_excel(
                job, file, job_pricing_id=job_pricing_id
            )
        except ValueError as exc:  # noqa: BLE001
            logger.error("Import error: %s", exc)
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "job_pricing_id": str(job_pricing.id),
            "parts_created": parts_created,
            "total_material_cost": str(material_cost),
            "total_adjustments_cost": str(adjustment_cost),
        }
        return Response(data, status=status.HTTP_201_CREATED)

