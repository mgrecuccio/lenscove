from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .cart import Cart
from store.models import Product


def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/detail.html", {"cart": cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    received_quantity = request.POST.get("quantity")

    quantity = get_quantity(received_quantity)

    override_flag = request.POST.get("override")
    override_quantity = override_flag in ("true", "True", "1", "on")

    dimension = request.POST.get("dimension")
    frame_type = request.POST.get("frame_type")
    frame_color = request.POST.get("frame_color")

    if override_quantity:
        if quantity <= 0:
            cart.remove(product)
        else:
            cart.add(
                product=product,
                quantity=quantity,
                override_quantity=True,
                dimension=dimension,
                frame_type=frame_type,
                frame_color=frame_color,
            )
    else:
        cart.add(
            product=product,
            quantity=quantity,
            override_quantity=False,
            dimension=dimension,
            frame_type=frame_type,
            frame_color=frame_color,
        )
        
        prod_key = str(product.id)
        if prod_key in cart.cart and cart.cart[prod_key]["quantity"] <= 0:
            cart.remove(product)
    
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart:cart_detail")


def get_quantity(received_quantity):
    try:
        quantity = int(received_quantity)
    except (TypeError, ValueError):
        quantity = 1
    return quantity
