# Generated by Django 5.1.5 on 2025-03-26 19:36

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workflow", "0107_purchaseorder_online_url_purchaseorder_raw_json"),
    ]

    operations = [
        migrations.AddField(
            model_name="xeroaccount",
            name="xero_last_synced",
            field=models.DateTimeField(
                blank=True, default=django.utils.timezone.now, null=True
            ),
        ),
    ]
