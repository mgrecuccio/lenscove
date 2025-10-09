from django.test import TestCase, override_settings
from orders.models import Order, OrderItem
from orders.utils import send_order_confirmation_email
from django.core import mail
from store.models import Product


@override_settings(DEFAULT_FROM_EMAIL='test_sender@example.com')
class SendOrderEmailTests(TestCase):


    def setUp(self):
        self.order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St',
            postal_code='12345',
            city='Anytown',
            paid=True
        )

        product = Product.objects.create(
            title='test-title',
            brand='test-brand',
            description='test-description',
            slug='test-slug',
            price=10.00
        )

        OrderItem.objects.create(
            order=self.order,
            product=product,
            quantity=2,
            price=product.price,
            dimensions='10x20',
            frame_color='black',
            frame_type='wood'
        )

    
    def test_send_order_confirmation_email(self):
        send_order_confirmation_email(self.order)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        self.assertEqual(email.subject, f'Order Confirmation - Order #{self.order.id}')

        self.assertEqual(email.to, [self.order.email])
        self.assertEqual(email.from_email, "test_sender@example.com")
