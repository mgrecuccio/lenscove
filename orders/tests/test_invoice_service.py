from django.test import TestCase
from PyPDF2 import PdfReader
from orders.models import Order, OrderItem
from store.models import Product
from orders.invoice_service import InvoiceService
import io


class TestInvoiceGeneration(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            title="Sample Photo",
            price=19.99,
            slug="sample-photo"
        )

        self.order = Order.objects.create(
            first_name="Marco",
            last_name="Test",
            email="marco@example.com",
            address="123 Street",
            postal_code="1000",
            city="Brussels",
        )

        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=self.product.price,
            quantity=2,
        )


    def test_generate_invoice_returns_pdf(self):
        buffer = InvoiceService.generate_invoice(self.order)

        self.assertIsInstance(buffer, io.BytesIO)
        content = buffer.getvalue()
        self.assertTrue(len(content) > 1000)


        pdf = PdfReader(buffer)
        self.assertGreater(len(pdf.pages), 0, "PDF should have at least 1 page")


        text = pdf.pages[0].extract_text()
        self.assertIn(f"Invoice #{self.order.id}", text)

        self.assertIn("Marco Test", text)

        self.assertIn("Sample Photo", text)
        self.assertIn("39.98", text)