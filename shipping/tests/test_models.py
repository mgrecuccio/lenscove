from django.test import TestCase
from django.core.files.base import ContentFile
from orders.models import Order
from shipping.models import Shipment
import time


class ShipmentModelTests(TestCase):

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


    def test_mark_label_created_sets_fields_and_saves_file(self):
        shipment = Shipment.objects.create(order=self.order)

        fake_pdf = ContentFile(b"%PDF-1.4\n%Fake PDF\n")

        self.addCleanup(lambda: shipment.label_pdf.delete(save=False) if shipment.label_pdf else None)

        shipment.mark_label_created(
            shippo_id="SHIPPO_ABC",
            tracking_number="TRACK123",
            tracking_url="http://goshippo.test/track/TRACK123",
            label_file=fake_pdf,
        )

        shipment.refresh_from_db()

        self.assertEqual(shipment.shippo_id, "SHIPPO_ABC")
        self.assertEqual(shipment.tracking_number, "TRACK123")
        self.assertEqual(shipment.tracking_url, "http://goshippo.test/track/TRACK123")
        self.assertEqual(shipment.status, "label_created")
       
        expected_filename = f"label_{shipment.id}"
        self.assertIn(expected_filename, shipment.label_pdf.name)
        self.assertTrue(shipment.label_pdf.name.endswith, ".pdf")
        self.assertGreater(shipment.label_pdf.size, 0)


    def test_update_status_changes_status_and_updated_timestamp(self):
        shipment = Shipment.objects.create(order=self.order)
        old_updated = shipment.updated

        time.sleep(0.01)
        shipment.update_status("in_transit")
        shipment.refresh_from_db()

        self.assertEqual(shipment.status, "in_transit")
        self.assertNotEqual(shipment.updated, old_updated)


    def test_str_returns_readable_description(self):
        shipment = Shipment.objects.create(order=self.order)
        expected = f"Shipment for Order {self.order.id} ({shipment.status})"
        self.assertEqual(str(shipment), expected)
