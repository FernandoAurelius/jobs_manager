# Generated by Django 5.1.5 on 2025-02-14 07:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workflow", "0080_historicaljob_complex_job_job_complex_job_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="companydefaults",
            name="last_xero_sync",
            field=models.DateTimeField(
                blank=True,
                help_text="The last time Xero data was synchronized",
                null=True,
            ),
        ),
    ]
