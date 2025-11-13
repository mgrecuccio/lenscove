from django.contrib import admin
from django.utils.html import format_html
from .models import Shipment
from .services import ShippingService


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "status",
        "tracking_number",
        "tracking_link",
        "label_link",
        "created",
        "updated",
    )
    readonly_fields = (
        "order",
        "shippo_id",
        "tracking_number",
        "tracking_url",
        "label_pdf",
        "created",
        "updated",
    )
    list_filter = ("status", "created", "updated")
    search_fields = ("order__id", "tracking_number")
    ordering = ("-created",)

    actions = ["generate_label"]

    def tracking_link(self, obj):
        if obj.tracking_url:
            return format_html('<a href="{}" target="_blank">Track</a>', obj.tracking_url)
        return "—"
    tracking_link.short_description = "Tracking"

    def label_link(self, obj):
        if obj.label_pdf:
            return format_html('<a href="{}" target="_blank">Download Label</a>', obj.label_pdf.url)
        return "—"
    label_link.short_description = "Label"

    @admin.action(description="Generate shipping label for selected shipments")
    def generate_label(self, request, queryset):
        success, failed = 0, 0
        for shipment in queryset:
            try:
                label_info = ShippingService.create_shippo_label(shipment.order)
                shipment.mark_label_created(
                    shippo_id=label_info["shippo_id"],
                    tracking_number=label_info["tracking_number"],
                    tracking_url=label_info["tracking_url"],
                    label_file=label_info["label_file"],
                )
                success += 1
            except Exception as e:
                failed += 1
                self.message_user(request, f"Error for order {shipment.order.id}: {e}", level="error")
        if success:
            self.message_user(request, f"{success} label(s) created successfully.")
        if failed:
            self.message_user(request, f"{failed} label(s) failed.", level="warning")
