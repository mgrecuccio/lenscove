from django.utils import timezone
from django.db import models
from orders.models import Order
from django.db import transaction


class Payment(models.Model):

    STATUS_CHOICES = [
        ("created", "Created"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("canceled", "Canceled"),
        ("expired", "Expired"),
        ("open", "Open"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    mollie_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="created")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    
    @transaction.atomic
    def mark_paid(self):
        self.status = "paid"
        self.updated = timezone.now()
        self.save(update_fields=['status', 'updated'])
        self.order.paid = True
        self.order.save(update_fields=['paid'])


    @transaction.atomic
    def mark_failed(self, status):
        self.status = status
        self.save(update_fields=["status"])


    def __str__(self):
        return f"Payment {self.mollie_id} ({self.status})"