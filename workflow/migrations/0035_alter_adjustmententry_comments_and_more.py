# Generated by Django 5.0.6 on 2024-11-16 08:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0034_alter_materialentry_quantity_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="adjustmententry",
            name="comments",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AlterField(
            model_name="adjustmententry",
            name="description",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AlterField(
            model_name="materialentry",
            name="comments",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AlterField(
            model_name="materialentry",
            name="description",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AlterField(
            model_name="materialentry",
            name="item_code",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
        migrations.AlterField(
            model_name="timeentry",
            name="date",
            field=models.DateField(
                blank=True,
                help_text="The date of the time entry.  Ie. the date the work was done.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="timeentry",
            name="description",
            field=models.TextField(default=""),
        ),
        migrations.AlterField(
            model_name="timeentry",
            name="is_billable",
            field=models.BooleanField(
                default=True,
                help_text="Set to false to avoid billing the client.  E.g. fixup work",
            ),
        ),
        migrations.AlterField(
            model_name="timeentry",
            name="job_pricing",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="time_entries",
                to="workflow.jobpricing",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="timeentry",
            name="mins_per_item",
            field=models.DecimalField(
                blank=True, decimal_places=2, default=0, max_digits=5
            ),
        ),
        migrations.AlterField(
            model_name="timeentry",
            name="staff",
            field=models.ForeignKey(
                blank=True,
                help_text="The Staff member who did the work.  Null for estimates/quotes.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="time_entries",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
