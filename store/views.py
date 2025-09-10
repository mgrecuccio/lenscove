from django.shortcuts import render
from django.shortcuts import get_object_or_404

from . models import Category, Product
from . models import ImageDimension, FrameType, FrameColor


def best_sellers(request):
    best_sellers = Product.objects.all()[0:4]
    context = {'best_sellers': best_sellers}
    return render(request, 'store/store.html', context)

def gallery(request):
    all_products = Product.objects.all()
    context = {'all_products': all_products}
    return render(request, 'store/gallery.html', context)


def categories(request):
    all_categories = Category.objects.all()
    return {'all_categories': all_categories}


def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)
    context = {
        'image_dimensions': ImageDimension,
        'frame_types': FrameType,
        'frame_colors': FrameColor,
        'product': product
    }
    return render(request, 'store/product-details.html', context)