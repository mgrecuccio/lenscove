from . import logging
from django.shortcuts import render
from .forms import OrderCreateForm
from .models import OrderItem
from cart.cart import Cart


def order_create(request):
    cart = Cart(request)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            logging.info(f"Creating order with data: {form.cleaned_data}")
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
            logging.info(f"Order {order.id} created successfully. Cart session cleared.")
            return render(request, 'orders/order_created.html', {"order": order})
    else:
        form = OrderCreateForm()

    return render(request, 'orders/order_create.html', {"cart": cart, "form": form})