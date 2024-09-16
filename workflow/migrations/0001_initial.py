# Generated by Django 5.0.6 on 2024-09-14 09:50

import uuid

import django.db.models.deletion
import django.utils.timezone
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Job",
            fields=[
                ("name", models.CharField(max_length=100)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("client_name", models.CharField(max_length=100)),
                (
                    "order_number",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("contact_person", models.CharField(max_length=100)),
                ("contact_phone", models.CharField(max_length=15)),
                ("job_number", models.CharField(blank=True, max_length=100, null=True)),
                ("description", models.TextField()),
                (
                    "date_created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("quoting", "Quoting"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("in_progress", "In Progress"),
                            ("on_hold", "On Hold"),
                            ("special", "Special"),
                            ("completed", "Completed"),
                            ("archived", "Archived"),
                        ],
                        default="quoting",
                        max_length=30,
                    ),
                ),
                ("paid", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Staff",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("first_name", models.CharField(max_length=30)),
                ("last_name", models.CharField(max_length=30)),
                (
                    "preferred_name",
                    models.CharField(blank=True, max_length=30, null=True),
                ),
                ("wage_rate", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "charge_out_rate",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("ims_payroll_id", models.CharField(max_length=100, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                (
                    "date_joined",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="HistoricalJob",
            fields=[
                ("name", models.CharField(max_length=100)),
                (
                    "id",
                    models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
                ),
                ("client_name", models.CharField(max_length=100)),
                (
                    "order_number",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("contact_person", models.CharField(max_length=100)),
                ("contact_phone", models.CharField(max_length=15)),
                ("job_number", models.CharField(blank=True, max_length=100, null=True)),
                ("description", models.TextField()),
                (
                    "date_created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("last_updated", models.DateTimeField(blank=True, editable=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("quoting", "Quoting"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("in_progress", "In Progress"),
                            ("on_hold", "On Hold"),
                            ("special", "Special"),
                            ("completed", "Completed"),
                            ("archived", "Archived"),
                        ],
                        default="quoting",
                        max_length=30,
                    ),
                ),
                ("paid", models.BooleanField(default=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical job",
                "verbose_name_plural": "historical jobs",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalStaff",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "id",
                    models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
                ),
                ("email", models.EmailField(db_index=True, max_length=254)),
                ("first_name", models.CharField(max_length=30)),
                ("last_name", models.CharField(max_length=30)),
                (
                    "preferred_name",
                    models.CharField(blank=True, max_length=30, null=True),
                ),
                ("wage_rate", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "charge_out_rate",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("ims_payroll_id", models.CharField(db_index=True, max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                (
                    "date_joined",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical staff",
                "verbose_name_plural": "historical staffs",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="JobPricingType",
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
                    "pricing_type",
                    models.CharField(
                        choices=[("fixed", "Fixed"), ("hourly", "Hourly")],
                        max_length=10,
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job_pricings",
                        to="workflow.job",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AdjustmentEntry",
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
                    "description",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                (
                    "cost",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                (
                    "revenue",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                (
                    "job_pricing_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="adjustment_entries",
                        to="workflow.jobpricingtype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MaterialEntry",
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
                ("description", models.CharField(max_length=200)),
                ("cost_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("sale_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("quantity", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "job_pricing_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="material_entries",
                        to="workflow.jobpricingtype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TimeEntry",
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
                ("date", models.DateField()),
                ("minutes", models.DecimalField(decimal_places=2, max_digits=5)),
                ("note", models.TextField(blank=True, null=True)),
                ("is_billable", models.BooleanField(default=True)),
                ("wage_rate", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "charge_out_rate",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="time_entries",
                        to="workflow.job",
                    ),
                ),
                (
                    "job_pricing",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="time_entries",
                        to="workflow.jobpricingtype",
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="time_entries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
