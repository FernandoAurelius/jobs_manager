# Generated by Django 5.1.5 on 2025-03-10 06:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0089_companydefaults_starting_job_number_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="staff",
            options={"ordering": ["last_name", "first_name"]},
        ),
    ]
