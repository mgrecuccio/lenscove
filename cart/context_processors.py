from .cart import Cart

def cart_length(request):
    return {'cart_length': Cart(request).total_quantity}