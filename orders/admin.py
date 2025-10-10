from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.html import format_html
from .models import Order, OrderItem
from .invoice import generate_invoice


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'paid', 'created', 'invoice_link']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]


    def invoice_link(self, obj):
        if obj.invoice_pdf:
            return format_html('<a href="{}" target="_blank">Download</a>', obj.invoice_pdf.url)
        return format_html('<a href="{}">Generate</a>', f"{obj.id}/generate-invoice/")
    invoice_link.short_description = "Invoice"


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:order_id>/generate-invoice/",
                self.admin_site.admin_view(self.generate_invoice_view),
                name="order-generate-invoice",
            ),
        ]
        return custom_urls + urls


    def generate_invoice_view(self, request, order_id):
        order = Order.objects.get(id=order_id)
        if order.invoice_pdf:
            return HttpResponseRedirect(order.invoice_pdf.url)

        pdf_buffer = generate_invoice(order)
        order.invoice_pdf.save(
            f"invoice_{order.id}.pdf",
            pdf_buffer,
            save=True
        )
        return HttpResponseRedirect(order.invoice_pdf.url)