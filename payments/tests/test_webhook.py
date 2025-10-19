from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from orders.models import Order
from payments.models import Payment
from decimal import Decimal
from payments.tests.factories import FakeMollieClient, FakeMolliePayment


class PaymentWebhookStatusTest(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            first_name="Jane", last_name="Roe", email="jane@example.com", paid=False
        )
        self.order.get_total_cost = lambda: Decimal("42.00")

    @patch("payments.views.get_mollie_client")
    def test_webhook_handles_failed_payment(self, mock_client_factory):
        fake_client = FakeMollieClient()
        mock_client_factory.return_value = fake_client

        payment = FakeMolliePayment(order_id=self.order.id, status="failed")
        fake_client._payments[payment.id] = payment
        Payment.objects.create(order=self.order, mollie_id=payment.id, amount=Decimal("42.00"))

        response = self.client.post(reverse("payments:mollie_webhook"), {"id": payment.id})
        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()
        self.assertFalse(self.order.paid)
        self.assertEqual(self.order.payment.status, "failed")
