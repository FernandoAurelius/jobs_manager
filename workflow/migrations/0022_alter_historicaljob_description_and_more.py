# Generated by Django 5.0.6 on 2024-11-05 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0021_alter_historicaljob_description_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicaljob",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="historicaljob",
            name="material_gauge_quantity",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="job",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="job",
            name="material_gauge_quantity",
            field=models.TextField(blank=True, null=True),
        ),
    ]