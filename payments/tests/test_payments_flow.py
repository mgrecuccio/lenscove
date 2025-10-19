from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from orders.models import Order
from payments.models import Payment
from decimal import Decimal
from payments.tests.factories import FakeMollieClient, FakeMolliePayment


class PaymentFlowTest(TestCase):
    
    def setUp(self):
        self.order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St',
            postal_code='12345',
            city='Anytown',
            paid=False
        )
        self.order.get_total_cost = lambda: Decimal("24.50")


    @patch("payments.services.get_mollie_client")
    def test_create_payment_redirects_to_checkout(self, mock_client_factory):
        fake_client = FakeMollieClient()
        mock_client_factory.return_value = fake_client

        response = self.client.get(reverse("payments:create_payment", args=[self.order.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("fake-mollie.test/checkout", response["Location"])

        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.status, "open")
        self.assertFalse(self.order.paid)

    
    @patch("payments.views.get_mollie_client")
    def test_webhook_marks_order_paid_and_generates_invoice(self, mock_client_factory):
        fake_client = FakeMollieClient()
        mock_client_factory.return_value = fake_client


        payment = FakeMolliePayment(order_id=self.order.id, status="paid")
        fake_client._payments[payment.id] = payment
        Payment.objects.create(order=self.order, mollie_id=payment.id, amount=Decimal("24.50"))

        response = self.client.post(reverse("payments:mollie_webhook"), {"id": payment.id})
        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()
        self.assertTrue(self.order.paid)
        self.assertTrue(self.order.invoice_pdf)
        self.assertEqual(self.order.payment.status, "paid")