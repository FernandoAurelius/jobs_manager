# Generated by Django 5.0.6 on 2024-11-21 20:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0041_timeentry_wage_rate_multiplier"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobpricing",
            name="job",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pricings",
                to="workflow.job",
            ),
        ),
    ]
