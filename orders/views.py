import logging
from django.http import Http404, FileResponse
from django.shortcuts import redirect, render
from .forms import OrderCreateForm
from .models import Order
from cart.cart import Cart
from .services import OrderService

logger = logging.getLogger(__name__)

def order_create(request):
    cart = Cart(request)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = OrderService.create_order_from_cart(form, cart)
            return redirect("payments:create_payment", order_id=order.id)
    else:
        form = OrderCreateForm()

    return render(request, 'orders/order_create.html', {"cart": cart, "form": form})


def order_invoice(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise Http404("Order does not exist")

    file_obj = OrderService.get_order_invoice(order)
    return FileResponse(file_obj, as_attachment=True, filename=f"invoice_{order.id}.pdf")
