from django.test import TestCase
from orders.models import Order, OrderItem
from django.db.models.fields import EmailField, BooleanField, CharField, DateTimeField, DecimalField, PositiveIntegerField
from payments.models import Payment
from decimal import Decimal

class PaymentModelTests(TestCase):
    
    def setUp(self):
        self.order = Order.objects.create(
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            address='12 Example Rd',
            postal_code='00000',
            city='Testville',
            paid=False,
        )

        self.payment = Payment.objects.create(
            order=self.order,
            mollie_id="tr_123",
            amount=Decimal("30.00"),
            status="created",
        )

    
    def test_mark_paid_sets_fields_and_updates_order_status(self):
        self.payment.mark_paid()
        self.payment.refresh_from_db()

        self.assertEqual(self.payment.status, "paid")
        self.assertTrue(self.order.paid)

    
    def test_mark_failed_updates_payment_status(self):
        self.payment.mark_failed("canceled")
        self.payment.refresh_from_db()

        self.assertEqual(self.payment.status, "canceled")
        self.assertFalse(self.order.paid)