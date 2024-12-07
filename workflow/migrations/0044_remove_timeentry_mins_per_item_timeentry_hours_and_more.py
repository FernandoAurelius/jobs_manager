# Generated by Django 5.0.6 on 2024-11-21 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0043_alter_jobpricing_job"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="timeentry",
            name="mins_per_item",
        ),
        migrations.AddField(
            model_name="timeentry",
            name="hours",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="timeentry",
            name="minutes",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="timeentry",
            name="minutes_per_item",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=5, null=True
            ),
        ),
        migrations.AlterField(
            model_name="timeentry",
            name="items",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
