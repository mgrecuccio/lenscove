from django.db import models
from orders.models import Order
from django.utils import timezone

class Shipment(models.Model):

    STATUS_CHOICES = [
        ("preparation", "Preparation"),
        ("label_created", "Label Created"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("error", "Error"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipment")
    shippo_id = models.CharField(max_length=100, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    tracking_url = models.URLField(blank=True, null=True)
    label_pdf = models.FileField(upload_to="shipping_labels/", blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="preparation")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def mark_label_created(self, shippo_id, tracking_number, tracking_url, label_file):
        self.shippo_id = shippo_id
        self.tracking_number = tracking_number
        self.tracking_url = tracking_url
        self.label_pdf.save(f"label_{self.id}.pdf", label_file)
        self.status = "label_created"
        self.updated = timezone.now()
        self.save()

    
    def update_status(self, new_status):
        self.status = new_status
        self.updated = timezone.now()
        self.save()

    
    def __str__(self):
        return f"Shipment for Order {self.order.id} ({self.status})"
