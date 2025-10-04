from . import logging
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from .cart import Cart
from store.models import Product

logger = logging.getLogger(__name__)


from cart.forms import AddToCartForm


@require_GET
def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/detail.html", {"cart": cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    form = AddToCartForm(request.POST)

    if form.is_valid():
        logger.info(f"Adding product {product_id} to cart with data: {form.cleaned_data}")
        cd = form.cleaned_data
        quantity=cd["quantity"]
        dimension=cd["dimension"]
        frame_type=cd["frame_type"]
        frame_color=cd["frame_color"]

        cart.add(
            product=product,
            quantity=quantity,
            override_quantity=False,
            dimension=dimension,
            frame_type=frame_type,
            frame_color=frame_color,
        )
    else:
        logger.warning(f"Invalid form data when adding product {product_id} to cart: {form.errors}")
    
    return redirect("cart:cart_detail")


@require_POST    
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if(cart.contains(product) == False):
        return redirect("cart:cart_detail")

    received_quantity = request.POST.get("quantity")
    quantity = get_quantity(received_quantity)

    if quantity <= 0:
        cart.remove(product)
    else:
        cart.add(
            product=product,
            quantity=quantity,
            override_quantity=True
        )

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