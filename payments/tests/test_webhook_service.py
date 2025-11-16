from unittest.mock import patch, MagicMock
from django.test import TestCase
from payments.webhook_service import WebhookService


class WebhookServiceTests(TestCase):
    
    @patch("payments.webhook_service.Order.objects.select_for_update")
    @patch("payments.webhook_service.Payment.objects.get")
    @patch("payments.webhook_service.WebhookService._mark_paid")
    def test_process_calls_mark_paid_for_successful_payment(self, mock_mark_paid, mock_payment_get, mock_select):
        order = MagicMock(id=1, paid=False)
        payment = MagicMock()
        mock_select.return_value.get.return_value = order
        mock_payment_get.return_value = payment

        payment_data = MagicMock()
        payment_data.metadata = {"order_id": 1}
        payment_data.is_paid.return_value = True
        payment_data.status = "paid"

        WebhookService.process(payment_data)

        mock_mark_paid.assert_called_once_with(order, payment)


    @patch("payments.services.Order.objects.select_for_update")
    @patch("payments.services.Payment.objects.get")
    def test_process_marks_failed_for_failed_payment(self, mock_payment_get, mock_select):
        order = MagicMock(id=1)
        payment = MagicMock()
        mock_select.return_value.get.return_value = order
        mock_payment_get.return_value = payment

        payment_data = MagicMock()
        payment_data.metadata = {"order_id": 1}
        payment_data.is_paid.return_value = False
        payment_data.status = "failed"

        WebhookService.process(payment_data)
        payment.mark_failed.assert_called_once_with("failed")

    
    @patch("shipping.services.ShippingService.create_shippo_label")
    @patch("shipping.models.Shipment.objects.create")
    @patch("orders.email_service.EmailService.send_order_confirmation_email")
    @patch("orders.invoice_service.InvoiceService.generate_invoice")
    @patch("django.core.mail.EmailMultiAlternatives.attach_file")
    def test_mark_paid_generates_invoice_and_creates_shipment(
        self, mock_attachment, mock_generate_invoice, mock_send_email, mock_create_shipment, mock_create_label
    ):
        order = MagicMock(id=10)
        order.email = "test@email.com"
        payment = MagicMock()

        pdf_buffer = MagicMock()
        pdf_buffer.read.return_value = b"pdf-bytes"
        mock_generate_invoice.return_value = pdf_buffer

        shipment = MagicMock()
        mock_create_shipment.return_value = shipment
        mock_create_label.return_value = {
            "shippo_id": "shp_123",
            "tracking_number": "TRACK123",
            "tracking_url": "http://track",
            "label_file": "label.pdf",
        }

        WebhookService._mark_paid(order, payment)

        payment.mark_paid.assert_called_once()
        order.mark_paid.assert_called_once()