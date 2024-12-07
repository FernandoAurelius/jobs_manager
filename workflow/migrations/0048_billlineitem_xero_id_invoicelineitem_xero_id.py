# Generated by Django 5.0.6 on 2024-11-22 03:22

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0047_rename_last_modified_bill_xero_last_modified_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="billlineitem",
            name="xero_line_id",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AddField(
            model_name="invoicelineitem",
            name="xero_line_id",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
