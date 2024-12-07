# Generated by Django 5.0.6 on 2024-12-06 07:37

import django.db.models.deletion
import uuid
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "workflow",
            "0057_rename_line_amount_billlineitem_line_amount_excl_tax_and_more",
        ),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="billlineitem",
            options={
                "verbose_name": "Bill Line Item",
                "verbose_name_plural": "Bill Line Items",
            },
        ),
        migrations.AlterModelOptions(
            name="invoicelineitem",
            options={
                "verbose_name": "Invoice Line Item",
                "verbose_name_plural": "Invoice Line Items",
            },
        ),
        migrations.RemoveField(
            model_name="billlineitem",
            name="tax_type",
        ),
        migrations.RemoveField(
            model_name="invoicelineitem",
            name="tax_type",
        ),
        migrations.CreateModel(
            name="CreditNote",
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
                ("xero_id", models.UUIDField(unique=True)),
                ("number", models.CharField(max_length=255)),
                ("date", models.DateField()),
                ("due_date", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Draft"),
                            ("SUBMITTED", "Submitted"),
                            ("AUTHORISED", "Authorised"),
                            ("DELETED", "Deleted"),
                            ("VOIDED", "Voided"),
                            ("PAID", "Paid"),
                        ],
                        default="DRAFT",
                        max_length=50,
                    ),
                ),
                (
                    "total_excl_tax",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("tax", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "total_incl_tax",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("amount_due", models.DecimalField(decimal_places=2, max_digits=10)),
                ("xero_last_modified", models.DateTimeField()),
                ("raw_json", models.JSONField()),
                ("django_created_at", models.DateTimeField(auto_now_add=True)),
                ("django_updated_at", models.DateTimeField(auto_now=True)),
                ("credit_note_number", models.CharField(max_length=20, unique=True)),
                ("reason", models.TextField(blank=True, null=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="workflow.client",
                    ),
                ),
            ],
            options={
                "verbose_name": "Credit Note",
                "verbose_name_plural": "Credit Notes",
                "ordering": ["-date"],
            },
        ),
        migrations.CreateModel(
            name="CreditLineItem",
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
                ("xero_line_id", models.UUIDField(default=uuid.uuid4, unique=True)),
                ("description", models.TextField()),
                (
                    "quantity",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        default=Decimal("1.00"),
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "unit_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "line_amount_excl_tax",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "line_amount_incl_tax",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "tax_amount",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "account",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="workflow.xeroaccount",
                    ),
                ),
                (
                    "credit_note",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="line_items",
                        to="workflow.creditnote",
                    ),
                ),
            ],
            options={
                "verbose_name": "Credit Note Line Item",
                "verbose_name_plural": "Credit Note Line Items",
            },
        ),
    ]
