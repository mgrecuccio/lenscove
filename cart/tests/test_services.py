from decimal import Decimal
from django.test import TestCase
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from store.models import Product, Category
from cart.cart import Cart
from cart.services import CartService


class MockSession(dict):
    modified = False

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.modified = True


class MockRequest:
    def __init__(self):
        self.session = MockSession()


class CartServicesTest(TestCase):
    def setUp(self):
        self.request = MockRequest()
        self.product = Product.objects.create(
            title="Mocked Product",
            slug="mocked-product",
            price=15.00,
            brand="Test Brand"
        )


    def test_add_product_to_cart_basic(self):
        cart = Cart(self.request)
        CartService.add_product_to_cart(cart, self.product, quantity=2)

        self.assertEqual(len(cart), 2)
        self.assertEqual(cart.total_quantity(), 2)
        self.assertEqual(cart.get_total_price(), Decimal("30.00"))
        cart.clear()


    def test_add_product_to_cart_with_options(self):
        cart = Cart(self.request)
        CartService.add_product_to_cart(
            cart,
            self.product,
            quantity=2,
            dimensions='large',
            frame_type='wood',
            frame_color='brown'
        )

        self.assertEqual(len(cart), 2)
        cart_item = list(cart)[0]
        self.assertEqual(cart_item['quantity'], 2)
        self.assertEqual(cart_item['dimensions'], '20x30')
        self.assertEqual(cart_item['frame_type'], 'wood')
        self.assertEqual(cart_item['frame_color'], 'brown')
        self.assertEqual(cart_item['total_price'], Decimal('30.00'))

    
    def test_update_quantity(self):
        cart = Cart(self.request)
        cart.add(self.product, quantity=1)
        cart.add(self.product, quantity=3, override_quantity=True)

        self.assertEqual(len(cart), 3)


    def test_update_cart_quantity_remove_on_zero(self):
        cart = Cart(self.request)

        CartService.add_product_to_cart(cart, self.product, quantity=1)
        CartService.update_cart_quantity(cart, self.product, received_quantity=0)

        self.assertEqual(len(cart), 0)