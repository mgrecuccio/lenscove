from django.shortcuts import render
from django.shortcuts import get_object_or_404
from cart.forms import AddToCartForm
from . models import Category, Product


def best_sellers(request):
    best_sellers = Product.objects.all()[0:4]
    context = {'best_sellers': best_sellers}
    return render(request, 'store/store.html', context)


def gallery(request, slug=None):
    if slug:
        try:
            selected_category = Category.objects.get(slug=slug)
            all_products = Product.objects.filter(category=selected_category)
        except Category.DoesNotExist:
            all_products = Product.objects.none()
    else:
        all_products = Product.objects.all()

    context = {
        'all_products': all_products,
        'current_category': slug,
    }
    return render(request, 'store/gallery.html', context)


def categories(request):
    all_categories = Category.objects.all()
    return {'all_categories': all_categories}


def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)

    form = AddToCartForm()

    return render(request, "store/product-details.html", {
        "product": product,
        "form": form,
    })