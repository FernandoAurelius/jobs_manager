# Generated by Django 5.2 on 2025-06-04 23:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("job", "0011_update_purchase_order_line_reference"),
        ("purchasing", "0004_stock"),
        ("workflow", "0154_auto_20250604_1054"),
    ]

    state_operations = [
        migrations.RemoveField(
            model_name="stock",
            name="job",
        ),
        migrations.RemoveField(
            model_name="stock",
            name="source_parent_stock",
        ),
        migrations.RemoveField(
            model_name="stock",
            name="source_purchase_order_line",
        ),
        migrations.DeleteModel(
            name="PurchaseOrder",
        ),
        migrations.DeleteModel(
            name="PurchaseOrderLine",
        ),
        migrations.DeleteModel(
            name="PurchaseOrderSupplierQuote",
        ),
        migrations.DeleteModel(
            name="Stock",
        ),
        migrations.CreateModel(
            name="Stock",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("purchasing.stock",),
        ),
    ]

    migrations.SeparateDatabaseAndState(
        state_operations=state_operations,
        database_operations=[],
    )
