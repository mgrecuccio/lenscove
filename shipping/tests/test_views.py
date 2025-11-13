import json
from django.test import TestCase
from unittest.mock import patch, Mock
from django.urls import reverse

class ShippingViewsTestCase(TestCase):
    

    def test_shippo_webhook_returns_400_for_invalid_json(self):
        url = reverse("shipping:shippo_webhook")
        data = {"invalid_json"}
        response = self.client.post(
            url,
            data=data,
            content_type="application/json"
        )   
        self.assertEqual(response.status_code, 400)


    @patch("shipping.views.WebhookService.handle_shippo_webhook", return_value=200)
    def test_handle_shippo_payload(self, mock_webhook_service):
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
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        mock_webhook_service.assert_called_once_with(shippo_payload)
