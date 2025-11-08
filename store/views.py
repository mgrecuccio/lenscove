from django.shortcuts import render
from cart.forms import AddToCartForm
from django.shortcuts import get_object_or_404
from . import services
from .models import Product


def best_sellers(request):
    best_sellers = services.StoreService.get_best_sellers()
    return render(request, 'store/store.html', {'best_sellers': best_sellers})


def gallery(request, slug=None):
    all_products = services.StoreService.get_products_by_category(slug)
    return render(request, 'store/gallery.html', {
        'all_products': all_products,
        'current_category': slug,
    })


def categories(request):
    return {'all_categories': services.StoreService.get_active_categories()}


def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, "store/product-details.html", {
        "product": product,
        "form": AddToCartForm(),
    })
