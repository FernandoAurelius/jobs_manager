import uuid
from django.db import models


class PurchaseOrder(models.Model):
    """A request to purchase materials from a supplier."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(
        "Client",
        on_delete=models.PROTECT,
        related_name="purchase_orders",
    )
    job = models.ForeignKey(
        "Job",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Primary job this PO is for",
    )
    po_number = models.CharField(max_length=50, unique=True)
    order_date = models.DateField()
    expected_delivery = models.DateField()
    xero_id = models.UUIDField(unique=True, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("submitted", "Submitted to Supplier"),
            ("partially_received", "Partially Received"),
            ("fully_received", "Fully Received"),
            ("void", "Voided"),
        ],
        default="draft",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def reconcile(self):
        """Check received quantities against ordered quantities."""
        for line in self.lines.all():
            total_received = sum(
                purchase_line.quantity for purchase_line in line.received_lines.all()
            )
            if total_received > line.quantity:
                return "Over"
            elif total_received < line.quantity:
                return "Partial"

        self.status = "fully_received"
        self.save()
        return "Reconciled"


class PurchaseOrderLine(models.Model):
    """A line item on a PO."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="lines"
    )
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    item_code = models.CharField(max_length=20, blank=True)
    received_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total quantity received against this line",
    )


class Purchase(models.Model):
    """Record of materials actually received."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(
        "Client", on_delete=models.PROTECT, related_name="purchases"
    )
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.PROTECT, null=True, blank=True
    )
    received_date = models.DateField()
    bill = models.ForeignKey(
        "Bill",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Associated Xero bill once reconciled",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PurchaseLine(models.Model):
    """Records what was actually received against a PO line"""

    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE, related_name="lines"
    )
    po_line = models.ForeignKey(
        PurchaseOrderLine, on_delete=models.PROTECT, related_name="received_lines"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Validate received quantity
        total_received = (
            sum(line.quantity for line in self.po_line.received_lines.all())
            + self.quantity
        )

        if total_received > self.po_line.quantity:
            raise ValueError(
                f"Total received ({total_received}) would exceed "
                f"ordered quantity ({self.po_line.quantity})"
            )
        super().save(*args, **kwargs)
