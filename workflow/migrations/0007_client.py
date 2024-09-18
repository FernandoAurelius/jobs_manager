# Generated by Django 5.0.6 on 2024-09-16 23:32

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0006_historicaljob_job_name_job_job_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Client",
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
                ("xero_contact_id", models.CharField(max_length=255, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                ("phone", models.CharField(blank=True, max_length=50, null=True)),
                ("address", models.TextField(blank=True, null=True)),
                ("is_account_customer", models.BooleanField(default=False)),
            ],
        ),
    ]