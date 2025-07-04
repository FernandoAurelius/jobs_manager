# Generated by Django 5.1.5 on 2025-03-26 06:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workflow", "0104_alter_purchaseorder_expected_delivery"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchaseorder",
            name="xero_last_modified",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="xero_last_synced",
            field=models.DateTimeField(
                blank=True, default=django.utils.timezone.now, null=True
            ),
        ),
    ]
