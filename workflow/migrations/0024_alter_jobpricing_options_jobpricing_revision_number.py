# Generated by Django 5.0.6 on 2024-11-05 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0023_alter_historicaljob_contact_phone_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="jobpricing",
            options={"ordering": ["-created_at", "pricing_stage"]},
        ),
        migrations.AddField(
            model_name="jobpricing",
            name="revision_number",
            field=models.PositiveIntegerField(
                default=1, help_text="Tracks the revision number for friendlier quotes"
            ),
        ),
    ]
