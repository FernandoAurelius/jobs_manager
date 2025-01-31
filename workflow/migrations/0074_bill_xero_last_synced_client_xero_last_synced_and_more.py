# Generated by Django 5.1.4 on 2025-01-31 15:01

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0073_jobpricing_is_historical"),
    ]

    operations = [
        migrations.AddField(
            model_name="bill",
            name="xero_last_synced",
            field=models.DateTimeField(
                blank=True, default=django.utils.timezone.now, null=True
            ),
        ),
        migrations.AddField(
            model_name="client",
            name="xero_last_synced",
            field=models.DateTimeField(
                blank=True, default=django.utils.timezone.now, null=True
            ),
        ),
        migrations.AddField(
            model_name="creditnote",
            name="xero_last_synced",
            field=models.DateTimeField(
                blank=True, default=django.utils.timezone.now, null=True
            ),
        ),
        migrations.AddField(
            model_name="invoice",
            name="xero_last_synced",
            field=models.DateTimeField(
                blank=True, default=django.utils.timezone.now, null=True
            ),
        ),
        migrations.AddField(
            model_name="xerojournal",
            name="xero_last_synced",
            field=models.DateTimeField(
                blank=True, default=django.utils.timezone.now, null=True
            ),
        ),
    ]
