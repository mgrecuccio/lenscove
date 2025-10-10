from django.test import TestCase
from store.models import Product
from orders.models import Order, OrderItem
from orders.invoice import generate_invoice


class InvoiceTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(
            title='test-title',
            brand='test-brand',
            description='test-description',
            slug='test-slug',
            price=9.99
        )

        cls.order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St',
            postal_code='12345',
            city='Anytown',
            paid=True
        )

        OrderItem.objects.create(
            order=cls.order,
            product=cls.product,
            quantity=2,
            price=cls.product.price,
            dimensions='10x20',
            frame_color='black',
            frame_type='wood'
        )

    
    def test_generate_invoice(self):
        buffer = generate_invoice(self.order)
        self.assertTrue(hasattr(buffer, "read"))

        data = buffer.read()
        self.assertGreater(len(data), 100)
        self.assertTrue(data.startswith(b"%PDF"))