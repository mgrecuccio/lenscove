from unittest.mock import patch, MagicMock
from django.test import TestCase
from payments.services import PaymentService
from payments.models import Payment
from orders.models import Order


class PaymentServiceTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            address="123 Test Street",
            postal_code="12345",
            city="Testville",
            paid=False,
        )


    @patch("payments.services.Client")
    @patch("payments.services.settings")
    def test_get_mollie_client_sets_api_key(self, mock_settings, mock_client):
        mock_settings.MOLLIE_API_KEY = "test-key"
        fake_client = MagicMock()
        mock_client.return_value = fake_client

        result = PaymentService.get_mollie_client()

        mock_client.assert_called_once()
        fake_client.set_api_key.assert_called_once_with("test-key")
        self.assertEqual(result, fake_client)


    @patch("payments.services.Payment.objects.create")
    @patch("payments.services.PaymentService.get_mollie_client")
    @patch("payments.services.settings")
    def test_create_payment_calls_mollie_and_creates_payment_record(
        self, mock_settings, mock_get_client, mock_payment_create
    ):
        mock_settings.MOLLIE_WEBHOOK_URL = "https://example.com/webhook"
        mock_settings.MOLLIE_REDIRECT_URL = "https://example.com/return"

        fake_mollie = MagicMock()
        mock_get_client.return_value = fake_mollie

        fake_payment = MagicMock()
        fake_payment.id = "tr_123"
        fake_payment.checkout_url = "https://mollie.com/checkout/tr_123"
        fake_mollie.payments.create.return_value = fake_payment

        self.order.get_total_cost = MagicMock(return_value=50.00)

        result = PaymentService.create_payment(self.order, request=MagicMock())

        fake_mollie.payments.create.assert_called_once_with({
            "amount": {"currency": "EUR", "value": "50.00"},
            "description": f"Order #{self.order.id}",
            "webhookUrl": "https://example.com/webhook",
            "redirectUrl": "https://example.com/return",
            "metadata": {"order_id": self.order.id},
        })

        fake_mollie.payments.update.assert_called_once_with(
            "tr_123",
            {"redirectUrl": "https://example.com/return?payment_id=tr_123"},
        )

        mock_payment_create.assert_called_once_with(
            order=self.order,
            mollie_id="tr_123",
            amount=50.00,
            status="open",
        )
        self.assertEqual(result, fake_payment)


    @patch("payments.services.PaymentService.get_mollie_client")
    @patch("payments.services.settings")
    def test_create_payment_logs_and_returns_on_error(self, mock_settings, mock_get_client):
        mock_settings.MOLLIE_WEBHOOK_URL = "https://webhook"
        mock_settings.MOLLIE_REDIRECT_URL = "https://redirect"

        fake_mollie = MagicMock()
        fake_mollie.payments.create.side_effect = Exception("API Error")
        mock_get_client.return_value = fake_mollie

        self.order.get_total_cost = MagicMock(return_value=99.00)

        with self.assertRaises(Exception):
            PaymentService.create_payment(self.order, request=MagicMock())
