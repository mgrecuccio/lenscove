import logging
from decimal import Decimal
from django.conf import settings
from store.models import Product

logger = logging.getLogger(__name__)

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    
    def add(self, product, quantity=1, override_quantity=False, dimensions=None, frame_type=None, frame_color=None):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
                'dimensions': dimensions,
                'frame_type': frame_type,
                'frame_color': frame_color,
            }
            logger.info(f"Product {product_id} added to cart")

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        # update options if provided
        if dimensions:
            self.cart[product_id]['dimensions'] = self.dimensions_label(dimensions)
        if frame_type:
            self.cart[product_id]['frame_type'] = frame_type
        if frame_color:
            self.cart[product_id]['frame_color'] = frame_color

        self.save()

    
    def save(self):
        self.session.modified = True

    
    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
            logger.info(f"Product {product_id} removed from cart")

    
    def contains(self, product):
        product_id = str(product.id)
        return product_id in self.cart


    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            item = self.cart[str(product.id)]
            item['product'] = product
            item['total_price'] = Decimal(item['price']) * item['quantity']
            yield item


    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
    

    def total_quantity(self):
        return sum(item['quantity'] for item in self.cart.values())


    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())


    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.save()


    def dimensions_label(self, dimensions):
        mapping = {
            'normal': '10x15',
            'medium': '13x18',
            'large': '20x30',
        }
        return mapping.get((dimensions or '').lower(), dimensions or '')