# Generated by Django 5.2 on 2025-05-06 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("workflow", "0138_stock_job_stock_source_purchase_order_line")]

    operations = [
        migrations.AddField(
            model_name="bill",
            name="xero_tenant_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="client",
            name="xero_tenant_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="creditnote",
            name="xero_tenant_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="invoice",
            name="xero_tenant_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="xero_tenant_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="quote",
            name="xero_tenant_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="xeroaccount",
            name="xero_tenant_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="xerojournal",
            name="xero_tenant_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="xeroaccount",
            name="account_name",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
