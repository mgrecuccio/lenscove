from . import logging
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from .cart import Cart
from store.models import Product
from .forms import AddToCartForm
from .services import CartService

logger = logging.getLogger(__name__)

@require_GET
def cart_detail(request) -> HttpResponse:
    cart = Cart(request)
    return render(request, "cart/detail.html", {"cart": cart})


@require_POST
def cart_add(request, product_id) -> HttpResponseRedirect:
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    form = AddToCartForm(request.POST)

    if form.is_valid():
        logger.info(f"Adding product {product_id} to cart with data: {form.cleaned_data}")
        cd = form.cleaned_data
        quantity=cd["quantity"]
        dimensions=cd["dimensions"]
        frame_type=cd["frame_type"]
        frame_color=cd["frame_color"]

        CartService.add_product_to_cart(
            cart=cart,
            product=product,
            quantity=quantity,
            override_quantity=False,
            dimensions=dimensions,
            frame_type=frame_type,
            frame_color=frame_color,
        )
    else:
        logger.warning(f"Invalid form data when adding product {product_id} to cart: {form.errors}")
    
    return redirect("cart:cart_detail")


@require_POST    
def cart_update(request, product_id) -> HttpResponseRedirect:
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if(cart.contains(product) == False):
        return redirect("cart:cart_detail")
    
    CartService.update_cart_quantity(cart, product, request.POST.get("quantity"))
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id) -> HttpResponseRedirect:
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