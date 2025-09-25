from decimal import Decimal
from django.test import TestCase
from store.models import Product
from cart.cart import Cart

class MockSession(dict):
    modified = False

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.modified = True


class MockRequest:
    def __init__(self):
        self.session = MockSession()


class CartUnitTest(TestCase):
    def setUp(self):
        self.request = MockRequest()
        self.product = Product.objects.create(
            title="Mocked Product",
            slug="mocked-product",
            price=15.00,
            brand="Test Brand"
        )


    def test_add_product(self):
        cart = Cart(self.request)
        cart.add(self.product, quantity=2)

        self.assertEqual(len(cart), 2)
        self.assertEqual(cart.total_quantity(), 2)
        self.assertEqual(cart.get_total_price(), Decimal("30.00"))


    def test_update_quantity(self):
        cart = Cart(self.request)
        cart.add(self.product, quantity=1)
        cart.add(self.product, quantity=3, override_quantity=True)

        self.assertEqual(len(cart), 3)


    def test_remove_product(self):
        cart = Cart(self.request)
        cart.add(self.product, quantity=1)
        cart.remove(self.product)

        self.assertEqual(len(cart), 0)


    def test_clear_cart(self):
        cart = Cart(self.request)
        cart.add(self.product, quantity=5)
        cart.clear()

        cart = Cart(self.request)  # reload from session
        self.assertEqual(len(cart), 0)
        self.assertTrue(self.request.session.modified)
