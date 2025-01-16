import logging
import mimetypes
import os
import uuid
from datetime import datetime
from typing import Dict, List

from django.db import models, transaction
from simple_history.models import HistoricalRecords  # type: ignore

from jobs_manager import settings
from workflow.models import CompanyDefaults

# We say . rather than workflow.models to avoid going through init,
# otherwise it would have a circular import
from .job_pricing import JobPricing
from .job_event import JobEvent

logger = logging.getLogger(__name__)


class Job(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)  # type: ignore

    id: uuid.UUID = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )  # type: ignore

    JOB_STATUS_CHOICES: List[tuple[str, str]] = [
        ("quoting", "Quoting"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("in_progress", "In Progress"),
        ("on_hold", "On Hold"),
        ("special", "Special"),
        ("completed", "Completed"),
        ("archived", "Archived"),
    ]

    STATUS_TOOLTIPS: Dict[str, str] = {
        "quoting": "The quote is currently being prepared.",
        "approved": "The quote has been approved, but work hasn't started yet.",
        "rejected": "The quote was declined.",
        "in_progress": "Work has started on this job.",
        "on_hold": "The job is on hold, possibly awaiting materials.",
        "special": "Shop jobs, upcoming shutdowns, etc.",
        "completed": "Work has finished on this job.",
        "archived": "The job has been paid for and picked up.",
    }

    client = models.ForeignKey(
        "Client",
        on_delete=models.SET_NULL,  # Option to handle if a client is deleted
        null=True,
        related_name="jobs",  # Allows reverse lookup of jobs for a client
    )
    order_number: str = models.CharField(
        max_length=100, null=True, blank=True
    )  # type: ignore
    contact_person: str = models.CharField(max_length=100)  # type: ignore
    contact_phone: str = models.CharField(  # type: ignore
        max_length=15,
        null=True,
        blank=True,
    )
    job_number: int = models.IntegerField(unique=True)  # Job 1234
    material_gauge_quantity: str = models.TextField(  # type: ignore
        blank=True,
        null=True,
        help_text="Internal notes such as the material to use.  Not shown on the invoice",
    )
    description: str = models.TextField(
        blank=True,
        null=True,
        help_text="This becomes the first line item on the invoice",
    )  # type: ignore

    quote_acceptance_date: datetime = models.DateTimeField(  # type: ignore
        null=True,
        blank=True,
    )
    delivery_date = models.DateField(null=True, blank=True)  # type: ignore
    status: str = models.CharField(
        max_length=30, choices=JOB_STATUS_CHOICES, default="quoting"
    )  # type: ignore
    # Decided not to bother with parent for now since we don't have a hierarchy of jobs.
    # Can be restored.
    # Parent would provide an alternative to historical records for tracking changes.
    # parent: models.ForeignKey = models.ForeignKey(
    #     "self",
    #     null=True,
    #     blank=True,
    #     related_name="revisions",
    #     on_delete=models.SET_NULL,
    # )
    # Shop job has no client (client_id is None)

    job_is_valid = models.BooleanField(default=False)  # type: ignore
    paid: bool = models.BooleanField(default=False)  # type: ignore
    charge_out_rate = (
        models.DecimalField(  # TODO: This needs to be added to the edit job form
            max_digits=10,
            decimal_places=2,
            null=False,  # Not nullable because save() ensures a value
            blank=False,  # Should be required in forms too
        )
    )

    # Direct relationships for estimate, quote, reality
    latest_estimate_pricing = models.OneToOneField(
        "JobPricing",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="latest_estimate_for_job",
    )

    latest_quote_pricing = models.OneToOneField(
        "JobPricing",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="latest_quote_for_job",
    )

    latest_reality_pricing = models.OneToOneField(
        "JobPricing",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="latest_reality_for_job",
    )

    archived_pricings = models.ManyToManyField(
        "JobPricing",
        related_name="archived_pricings_for_job",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history: HistoricalRecords = HistoricalRecords()

    class Meta:
        ordering = ["job_number"]

    @property
    def shop_job(self) -> bool:
        """Indicates if this is a shop job (no client)."""
        return (
            str(self.client_id) == "00000000-0000-0000-0000-000000000001"
        )  # This is the UUID for the shop client

    def __str__(self) -> str:
        client_name = self.client.name if self.client else "No Client"
        job_name = self.name if self.name else "No Job Name"
        return f" {self.job_number} - {job_name} for {client_name}"

    def get_display_name(self) -> str:
        return f"Job: {self.job_number}"  # type: ignore

    def save(self, *args, **kwargs):
        staff = kwargs.pop("staff", None)

        is_new = self._state.adding
        original_status = None if is_new else Job.objects.get(pk=self.pk).status

        # Step 1: Check if this is a new instance (based on `self._state.adding`)
        if not self.job_number:
            self.job_number = self.generate_unique_job_number()
            logger.debug(f"Saving job with job number: {self.job_number}")
        if self.charge_out_rate is None:
            company_defaults = CompanyDefaults.objects.first()
            self.charge_out_rate = company_defaults.charge_out_rate

        if (
            staff
            and not JobEvent.objects.filter(job=self, event_type="created").exists()
        ):
            JobEvent.objects.create(
                job=self,
                event_type="created",
                description=f"Job {self.name} created",
                staff=staff,
            )

        if is_new:
            # Creating a new job is tricky because of the circular reference.
            # We first save the job to the DB without any associated pricings, then we
            super(Job, self).save(*args, **kwargs)

            # Lazy import JobPricing using Django's apps.get_model()
            # We need to do this because of circular imports.  JobPricing imports Job

            #  Create the initial JobPricing instances
            logger.debug("Creating related JobPricing entries.")
            self.latest_estimate_pricing = JobPricing.objects.create(
                pricing_stage="estimate", job=self
            )
            self.latest_quote_pricing = JobPricing.objects.create(
                pricing_stage="quote", job=self
            )
            self.latest_reality_pricing = JobPricing.objects.create(
                pricing_stage="reality", job=self
            )
            logger.debug("Initial pricings created successfully.")

            # Save the references back to the DB
            super(Job, self).save(
                update_fields=[
                    "latest_estimate_pricing",
                    "latest_quote_pricing",
                    "latest_reality_pricing",
                ]
            )

        else:
            if original_status != self.status and staff:
                JobEvent.objects.create(
                    job=self,
                    event_type="status_change",
                    description=f"Job status changed from {original_status} to {self.status}",
                    staff=staff,
                )

            # Step 5: Save the Job to persist everything, including relationships
            super(Job, self).save(*args, **kwargs)

    @staticmethod
    def generate_unique_job_number():
        with transaction.atomic():
            last_job = Job.objects.select_for_update().order_by("-job_number").first()
            if last_job and last_job.job_number:
                return last_job.job_number + 1
            return 1  # Start numbering from 1 if there are no existing records
