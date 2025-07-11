# Generated by Django 5.2 on 2025-06-02 06:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("job", "0007_fix_jobpart_state"),
    ]

    operations = [
        # JobPart options and job_pricing field already correct from creation
        migrations.AddField(
            model_name="jobpricing",
            name="default_part",
            field=models.OneToOneField(
                blank=True,
                help_text="The default 'Main Work' part associated with this JobPricing instance. This part typically holds general time and material entries for the given pricing type.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="default_for_job_pricing",
                to="job.jobpart",
            ),
        ),
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
            model_name="historicaljob",
            name="created_at",
            field=models.DateTimeField(blank=True, editable=False),
        ),
        migrations.AlterField(
            model_name="historicaljob",
            name="updated_at",
            field=models.DateTimeField(blank=True, editable=False),
        ),
        # JobPart name field already correct from creation
    ]
