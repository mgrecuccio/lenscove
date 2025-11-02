import logging
from django.http import Http404, FileResponse
from django.shortcuts import redirect, render
from .forms import OrderCreateForm
from .models import Order, OrderItem
from cart.cart import Cart
from .invoice import generate_invoice

logger = logging.getLogger(__name__)

def order_create(request):
    cart = Cart(request)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            logger.info(f"Creating order with data: {form.cleaned_data}")
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['product'].price,
                    quantity=item['quantity'],
                    dimensions=item.get('dimensions', 'normal'),
                    frame_type=item.get('frame_type', 'plastic'),
                    frame_color=item.get('frame_color', 'black')
            )
            cart.clear()
            return redirect("payments:create_payment", order_id=order.id)
    else:
        form = OrderCreateForm()

    return render(request, 'orders/order_create.html', {"cart": cart, "form": form})


def order_invoice(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        logger.info(f"Generating downloadable invoice for order {order_id}")
    except Order.DoesNotExist:
        logger.error(f"Order with id {order_id} does not exist.")
        raise Http404("Order does not exist")
    
    if order.invoice_pdf:
        return FileResponse(open(order.invoice_pdf.path, "rb"), as_attachment=True)
    else:
        pdf_buffer = generate_invoice(order)
        return FileResponse(pdf_buffer, as_attachment=True, filename=f"invoice_{order.id}.pdf")