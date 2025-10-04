from django.contrib import admin
from . models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'created', 'paid', 'get_total_cost']
    search_fields = ['id', 'email', 'first_name', 'last_name', 'address', 'city', 'postal_code']
    list_filter = ['paid', 'created']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price']
    search_fields = ['order__id', 'product__title']
    list_filter = ['order__paid']
    