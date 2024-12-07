# Generated by Django 5.0.6 on 2024-11-22 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0053_alter_job_latest_estimate_pricing_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicaljob",
            name="shop_job",
        ),
        migrations.RemoveField(
            model_name="job",
            name="shop_job",
        ),
        migrations.AlterField(
            model_name="historicaljob",
            name="description",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="historicaljob",
            name="material_gauge_quantity",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Description of material gauge and quantity requirements",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="job",
            name="description",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="job",
            name="material_gauge_quantity",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Description of material gauge and quantity requirements",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="timeentry",
            name="wage_rate_multiplier",
            field=models.DecimalField(
                decimal_places=2,
                default=1,
                help_text="Multiplier for hourly rate. Example: 2.0 for double time. 0 means no paid. 1 means normal rate.",
                max_digits=5,
            ),
        ),
    ]
