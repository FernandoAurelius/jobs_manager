# Generated by Django 5.0.6 on 2024-11-21 22:36

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workflow", "0045_remove_timeentry_minutes"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="bill",
            options={
                "ordering": ["-date", "number"],
                "verbose_name": "Bill",
                "verbose_name_plural": "Bills",
            },
        ),
        migrations.AlterModelOptions(
            name="client",
            options={"ordering": ["name"]},
        ),
        migrations.AlterModelOptions(
            name="invoice",
            options={
                "ordering": ["-date", "number"],
                "verbose_name": "Invoice",
                "verbose_name_plural": "Invoices",
            },
        ),
        migrations.RenameField(
            model_name="client",
            old_name="last_modified",
            new_name="django_updated_at",
        ),
        migrations.AddField(
            model_name="bill",
            name="django_created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="bill",
            name="django_updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="client",
            name="django_created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="invoice",
            name="django_created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="invoice",
            name="django_updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="xeroaccount",
            name="django_created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="xeroaccount",
            name="django_updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
