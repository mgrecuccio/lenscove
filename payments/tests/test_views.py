from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from orders.models import Order
from django.http import HttpResponse


class PaymentViewsTest(TestCase):
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


    @patch("payments.views.PaymentService.create_payment")
    def test_create_payment_redirects_to_checkout_url(self, mock_create_payment):
        mock_payment = MagicMock()
        mock_payment.checkout_url = "https://mollie.test/checkout/123"
        mock_create_payment.return_value = mock_payment

        url = reverse("payments:create_payment", args=[self.order.id])
        response = self.client.get(url)

        self.assertRedirects(response, "https://mollie.test/checkout/123", fetch_redirect_response=False)
        mock_create_payment.assert_called_once()
        args, kwargs = mock_create_payment.call_args
        self.assertEqual(args[0], self.order)


    def test_mollie_webhook_returns_400_if_missing_payment_id(self):
        url = reverse("payments:mollie_webhook")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)


    @patch("payments.views.WebhookService.process")
    @patch("payments.views.PaymentService.get_mollie_client")
    def test_mollie_webhook_happy_flow(self, mock_get_mollie_client, mock_process):
        payment_id = "tr_test123"

        mock_mollie = MagicMock()
        mock_payment_data = {"id": payment_id, "status": "paid"}
        mock_mollie.payments.get.return_value = mock_payment_data
        mock_get_mollie_client.return_value = mock_mollie

        url = reverse("payments:mollie_webhook")
        data = {"id": payment_id}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        mock_mollie.payments.get.assert_called_once_with(payment_id)
        mock_process.assert_called_once_with(mock_payment_data)

    
    def test_payment_return_webhook_returns_400_if_missing_payment_id(self):
        url = reverse("payments:payment_return")
        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)


    @patch("payments.views.PaymentService.get_mollie_client")
    def test_payment_return_webhook_redirects_to_pending_payment_if_oder_unpaid(self, mock_get_mollie_client):
        payment_id = "tr_test123"

        mock_mollie = MagicMock()
        mock_payment_data = MagicMock()
        mock_payment_data.metadata = {"order_id": self.order.id}
        mock_mollie.payments.get.return_value = mock_payment_data
        mock_get_mollie_client.return_value = mock_mollie

        url = reverse("payments:payment_return")
        data = {"payment_id": payment_id}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, 200)
        mock_mollie.payments.get.assert_called_once_with(payment_id)
        self.assertTemplateUsed(response, 'payments/payment_pending.html')


    @patch("payments.views.PaymentService.get_mollie_client")
    def test_payment_return_webhook_redirects_to_order_created_if_oder_paid(self, mock_get_mollie_client):
        self.order.mark_paid()
        payment_id = "tr_test123"
        
        mock_mollie = MagicMock()
        mock_payment_data = MagicMock()
        mock_payment_data.metadata = {"order_id": self.order.id}
        mock_mollie.payments.get.return_value = mock_payment_data
        mock_get_mollie_client.return_value = mock_mollie

        url = reverse("payments:payment_return")
        data = {"payment_id": payment_id}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, 200)
        mock_mollie.payments.get.assert_called_once_with(payment_id)
        self.assertTemplateUsed(response, 'orders/order_created.html')