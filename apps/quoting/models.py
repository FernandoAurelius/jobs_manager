import uuid
from django.db import models
from django.utils import timezone

from apps.client.models import Client


class SupplierProduct(models.Model):
    """
    Products scraped from supplier websites for pricing/availability lookup.
    This is NOT our internal product catalog - it's external supplier data.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="scraped_products"
    )
    price_list = models.ForeignKey(
        "SupplierPriceList", on_delete=models.CASCADE, related_name="products"
    )
    product_name = models.CharField(max_length=500)
    item_no = models.CharField(max_length=100, help_text="Supplier's item/SKU number")
    description = models.TextField(blank=True, null=True)
    specifications = models.TextField(blank=True, null=True)
    variant_id = models.CharField(
        max_length=100, help_text="Unique variant identifier from supplier"
    )
    variant_width = models.CharField(max_length=50, blank=True, null=True)
    variant_length = models.CharField(max_length=50, blank=True, null=True)
    variant_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_unit = models.CharField(
        max_length=50, blank=True, null=True, help_text="e.g., 'per metre', 'each'"
    )
    variant_available_stock = models.IntegerField(blank=True, null=True)
    url = models.URLField(
        max_length=1000, help_text="Direct URL to this product on supplier's website"
    )

    # Standard audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["supplier", "url", "item_no", "variant_id"]
        indexes = [
            models.Index(fields=["variant_id"]),
            models.Index(fields=["item_no"]),
            models.Index(fields=["url"]),
            models.Index(fields=["product_name"]),
        ]

    def __str__(self):
        return f"{self.supplier.name} - {self.product_name} - {self.variant_id}"


class SupplierPriceList(models.Model):
    """
    Represents a specific import of a supplier's price list.J
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="price_lists"
    )
    file_name = models.CharField(
        max_length=255, help_text="Original filename of the uploaded price list"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Supplier Price List"
        verbose_name_plural = "Supplier Price Lists"

    def __str__(self):
        return f"{self.supplier.name} - {self.file_name} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"


class ScrapeJob(models.Model):
    """
    Tracks scraping job execution for monitoring and preventing concurrent runs.
    """
    
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="scrape_jobs"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    products_scraped = models.IntegerField(default=0)
    products_failed = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Scrape Job"
        verbose_name_plural = "Scrape Jobs"
    
    def __str__(self):
        return f"{self.supplier.name} - {self.status} ({self.started_at.strftime('%Y-%m-%d %H:%M')})"
