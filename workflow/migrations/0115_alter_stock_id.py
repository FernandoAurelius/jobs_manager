# Generated by Django 5.1.5 on 2025-04-03 07:36

import uuid
import django.utils.timezone
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0114_stock_is_active"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # Drop any lingering foreign-key constraints before dropping the table
                migrations.RunSQL(
                    "ALTER TABLE workflow_materialentry DROP FOREIGN KEY workflow_materialent_source_stock_id_016e8e14_fk_workflow_;"
                ),
                migrations.RunSQL(
                    "ALTER TABLE workflow_stock DROP FOREIGN KEY workflow_stock_source_parent_stock__7633cf27_fk_workflow_;"
                ),
                # Finally drop the old table if it exists
                migrations.RunSQL("DROP TABLE IF EXISTS workflow_stock;")
            ],
            state_operations=[
                migrations.DeleteModel(name="Stock"),
            ],
        ),
        # Recreate Stock with new UUID PK and no FKs
        migrations.CreateModel(
            name="Stock",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("description", models.CharField(help_text="Description of the stock item", max_length=255)),
                ("quantity", models.DecimalField(decimal_places=2, help_text="Current quantity of the stock item", max_digits=10)),
                ("unit_cost", models.DecimalField(decimal_places=2, help_text="Cost per unit of the stock item", max_digits=10)),
                ("date", models.DateTimeField(default=django.utils.timezone.now, help_text="Date the stock item was created")),
                ("source", models.CharField(
                    choices=[
                        ("purchase_order", "Purchase Order Receipt"),
                        ("split_from_stock", "Split/Offcut from Stock"),
                        ("manual", "Manual Adjustment/Stocktake")
                    ], help_text="Origin of this stock item", max_length=50
                )),
                ("notes", models.TextField(blank=True, help_text="Additional notes about the stock item")),
                ("is_active", models.BooleanField(db_index=True, default=True, help_text="False when quantity reaches zero or item is fully consumed/transformed")),
            ],
        ),
    ]
