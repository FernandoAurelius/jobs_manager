# Generated by Django 5.0.6 on 2024-09-17 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0008_client_last_modified"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="raw_json",
            field=models.JSONField(blank=True, null=True),
        ),
    ]