import json
from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from orders.models import Order
from shipping.models import Shipment


class ShippoWebhookTest(TestCase):

    def setUp(self):
        self.order = Order.objects.create(
            first_name = "John",
            last_name = "Doe",
            email = "john@example.com",
            address = "Test Street 1",
            postal_code = "12345",
            city = "Brussels",
            paid = True,
        )

        self.shipment = Shipment.objects.create(
            order = self.order,
            tracking_number = "SHIPPO_DELIVERED",
            tracking_url = "https://goshippo.com/track/SHIPPO_DELIVERED",
            status = "preparation"
        )

        self.client = Client()
        self.url = reverse("shippo_webhook")


    def _build_payload(self, status="DELIVERED"):
        return {
            "event": "track_update",
            "data": {
                "tracking_number": self.shipment.tracking_number,
                "tracking_status": {
                    "status": status,
                    "status_details": "Your shipment has been delivered."
                },
            },
        }
    
    def test_webhook_updates_shipment_status(self):
        payload = self._build_payload("DELIVERED")

        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        self.shipment.refresh_from_db()
        self.assertEqual(self.shipment.status, "DELIVERED")


    def test_webhook_email(self):
        payload = self._build_payload("IN_TRANSIT")

        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn("IN_TRANSIT", email.subject)
        self.assertIn(self.order.email, email.to)


    def test_webhook_unkown_tracking_number(self):
        payload = self._build_payload()

        payload["data"]["tracking_number"] = "UNKNOWN_TRACKING"

        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)