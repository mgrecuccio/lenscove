from django.test import TestCase
from unittest.mock import patch, Mock
from orders.models import Order
from shipping.services import ShippingService


class CreateShippoLabelTests(TestCase):


    def setUp(self):
        self.order = Order.objects.create(
            first_name='Alice',
            last_name='Smith',
            email='alice@example.com',
            address='1 Test Lane',
            postal_code='11111',
            city='Test City',
            paid=False,
        )


    @patch('shipping.services.requests.get')
    @patch('shipping.services.shippo_sdk')
    def test_create_shippo_label_success(self, mock_shippo_sdk, mock_requests_get):
        fake_rate = Mock()
        fake_rate.object_id = 'RATE_1'
        fake_shipment = Mock()
        fake_shipment.rates = [fake_rate]

        fake_transaction = Mock()
        fake_transaction.status = 'SUCCESS'
        fake_transaction.object_id = 'TRANS_123'
        fake_transaction.tracking_number = 'TRACK123'
        fake_transaction.tracking_url_provider = 'http://carrier.test/track/TRACK123'
        fake_transaction.label_url = 'http://labels.test/label.pdf'

        mock_shippo_sdk.shipments.create.return_value = fake_shipment
        mock_shippo_sdk.transactions.create.return_value = fake_transaction

        fake_response = Mock()
        fake_response.content = b"%PDF-1.4\n%Fake PDF\n"
        mock_requests_get.return_value = fake_response

        result = ShippingService.create_shippo_label(self.order)

        self.assertIsInstance(result, dict)
        self.assertEqual(result['shippo_id'], 'TRANS_123')
        self.assertEqual(result['tracking_number'], 'TRACK123')
        self.assertEqual(result['tracking_url'], 'http://carrier.test/track/TRACK123')
        self.assertIn('label_file', result)

        label = result['label_file']
        self.assertTrue(hasattr(label, 'read'))
        label.seek(0)
        content = label.read()
        self.assertEqual(content, b"%PDF-1.4\n%Fake PDF\n")

        mock_requests_get.assert_called_once_with('http://labels.test/label.pdf', timeout=30)


    @patch('shipping.services.shippo_sdk')
    def test_create_shippo_label_transaction_failure_raises(self, mock_shippo_sdk):
        fake_rate = Mock()
        fake_rate.object_id = 'RATE_1'
        fake_shipment = Mock()
        fake_shipment.rates = [fake_rate]

        fake_transaction = Mock()
        fake_transaction.status = 'FAILURE'
        fake_transaction.messages = 'Some error from Shippo'

        mock_shippo_sdk.shipments.create.return_value = fake_shipment
        mock_shippo_sdk.transactions.create.return_value = fake_transaction

        with self.assertRaises(Exception) as ctx:
            ShippingService.create_shippo_label(self.order)

        self.assertIn('Shippo label creation failed', str(ctx.exception))
