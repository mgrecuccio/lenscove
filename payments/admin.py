from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "status", "created", "updated")
    list_filter = ("status", "created")
    search_fields = ("order__id", "mollie_id")
