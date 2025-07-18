# Generated by Django 5.2 on 2025-06-19 15:54

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("job", "0026_alter_historicaljob_status_alter_job_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="QuoteSpreadsheet",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "sheet_id",
                    models.CharField(help_text="Google Drive file ID", max_length=100),
                ),
                ("sheet_url", models.URLField(blank=True, max_length=500, null=True)),
                (
                    "tab",
                    models.CharField(
                        blank=True, default="Primary Details", max_length=100, null=True
                    ),
                ),
                (
                    "job",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quote_sheet",
                        to="job.job",
                    ),
                ),
            ],
            options={
                "verbose_name": "Quote Spreadsheet",
                "verbose_name_plural": "Quote Spreadsheets",
            },
        ),
    ]
