# Generated by Django 5.0.6 on 2024-11-16 04:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0032_alter_job_latest_estimate_pricing_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="jobpricing",
            name="job",
        ),
        migrations.AlterField(
            model_name="job",
            name="latest_estimate_pricing",
            field=models.OneToOneField(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="latest_estimate_for_job",
                to="workflow.jobpricing",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="job",
            name="latest_quote_pricing",
            field=models.OneToOneField(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="latest_quote_for_job",
                to="workflow.jobpricing",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="job",
            name="latest_reality_pricing",
            field=models.OneToOneField(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="latest_reality_for_job",
                to="workflow.jobpricing",
            ),
            preserve_default=False,
        ),
    ]