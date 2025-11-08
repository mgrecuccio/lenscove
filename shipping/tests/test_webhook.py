import json
from django.test import TestCase
from django.urls import reverse
from orders.models import Order
from shipping.models import Shipment
from django.test import override_settings
from django.core import mail
from shipping.webhook_service import WebhookService
from unittest.mock import MagicMock, patch
from django.core.files.base import ContentFile


class ShippoWebhookTest(TestCase):
    
    @patch("shipping.webhook_service.WebhookService._notify_customer")
    def test_shippo_webhook_returns_400_if_missing_tracking_number(self, mock_notify_customer):
        shippo_payload = {
            "event": "tracking_update",
            "data": {
                "tracking_status": {"status": "DELIVERED"}
            }
        }
        url = reverse("shipping:shippo_webhook")

        response = self.client.post(
            url,
            data=json.dumps(shippo_payload),
            content_type = "application/json"
        )

        self.assertEqual(response.status_code, 400)
        mock_notify_customer.assert_not_called()


    @patch("shipping.webhook_service.WebhookService._notify_customer")
    def test_shippo_webhook_returns_404_if_shipment_not_found(self, mock_notify_customer):
        shippo_payload = {
            "event": "tracking_update",
            "data": {
                "tracking_number": "1223344RR",
                "tracking_status": {"status": "DELIVERED"}
            }
        }
        url = reverse("shipping:shippo_webhook")

        response = self.client.post(
            url,
            data=json.dumps(shippo_payload),
            content_type = "application/json"
        )

        self.assertEqual(response.status_code, 404)
        mock_notify_customer.assert_not_called()


    @patch("shipping.webhook_service.Shipment.objects.get")
    @patch("shipping.webhook_service.WebhookService._notify_customer")
    def test_shippo_webhook_returns_200_if_no_new_status_is_received_from_shippo(
        self, mock_notify_customer, mock_shipment
    ):

        fake_shipment = MagicMock()
        mock_shipment.return_value = fake_shipment
        tracking_number = "1223344RR"

        shippo_payload = {
            "event": "tracking_update",
            "data": {
                "tracking_number": tracking_number,
            }
        }
        url = reverse("shipping:shippo_webhook")

        response = self.client.post(
            url,
            data=json.dumps(shippo_payload),
            content_type = "application/json"
        )

        self.assertEqual(response.status_code, 200)
        mock_notify_customer.assert_not_called()
        mock_shipment.assert_called_once_with(tracking_number=tracking_number)


    @override_settings(MEDIA_ROOT="/tmp/test_media")
    @patch("shipping.webhook_service.WebhookService._notify_customer")
    def test_shipment_status_update_and_customer_notified(
        self, mock_notify_customer
    ):
        fake_tracking_number = "1223344RR"
        fake_new_status="DELIVERED"

        order = Order.objects.create(
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            address='12 Example Rd',
            postal_code='00000',
            city='Testville',
            paid=False,
        )
        
        shipment = Shipment.objects.create(order=order)
        shipment.mark_label_created(
            "shippo_id_1",
            fake_tracking_number,
            "http://fake-shippo-tracking-url.com",
            ContentFile(b"fake pdf content", name="fake_label_file.pdf"),
        )

        self.assertEqual(shipment.status, "label_created")
        url = reverse("shipping:shippo_webhook")

        shippo_payload = {
            "event": "tracking_update",
            "data": {
                "tracking_number": shipment.tracking_number,
                "tracking_status": {"status": fake_new_status}
            }
        }

        response = self.client.post(
            url,
            data=json.dumps(shippo_payload),
            content_type="application/json"
        )

        shipment.refresh_from_db()
        self.assertEqual(shipment.status, fake_new_status)
        self.assertEqual(response.status_code, 200)
        mock_notify_customer.assert_called_once_with(shipment, fake_new_status)
        
    
    def test_notify_customer_sends_real_email_in_outbox(self):
        order = MagicMock(id=3, email="susan@example.com")
        shipment = MagicMock(id=7, order=order, tracking_url="http://track")
        WebhookService._notify_customer(shipment, "DELIVERED")

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn("DELIVERED", email.subject)
        self.assertIn("http://track", email.body)
        self.assertEqual(email.to, ["susan@example.com"])