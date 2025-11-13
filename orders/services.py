import logging
from django.db import transaction
from cart.cart import Cart
from .models import Order, OrderItem
from .invoice_service import InvoiceService

logger = logging.getLogger(__name__)

class OrderService:

    @staticmethod
    @transaction.atomic
    def create_order_from_cart(form, cart: Cart) -> Order:
        logger.info(f"Creating order with data: {form.cleaned_data}")
        order = form.save()

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                price=item["product"].price,
                quantity=item["quantity"],
                dimensions=item.get("dimensions", "normal"),
                frame_type=item.get("frame_type", "plastic"),
                frame_color=item.get("frame_color", "black"),
            )

        cart.clear()
        logger.info(f"Order #{order.id} created successfully with {order.items.count()} items")
        return order


    @staticmethod
    def get_order_invoice(order: Order):
        if order.invoice_pdf:
            logger.info(f"Serving existing invoice for order {order.id}")
            return open(order.invoice_pdf.path, "rb")

        logger.info(f"Generating new invoice for order {order.id}")
        return InvoiceService.generate_invoice(order)
