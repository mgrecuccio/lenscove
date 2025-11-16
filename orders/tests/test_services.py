from unittest.mock import MagicMock, patch
from django.test import TestCase
from store.models import Product
from orders.services import OrderService
from orders.models import Order,OrderItem

class OrderServiceTests(TestCase):


    def setUp(self):
        self.product = Product.objects.create(
            title='test-title',
            brand='test-brand',
            description='test-description',
            slug='test-slug',
            price=10.00
        )


    @patch("orders.services.InvoiceService.generate_invoice")
    def test_create_order_from_cart_creates_items_and_clears_cart(
        self, mock_generate_invoice
    ):
        form = MagicMock()
        form.cleaned_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "address": "123 Test Street",
            "postal_code": "12345",
            "city": "TestCity",
        }

        order = Order.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            address="123 Test Street",
            postal_code="12345",
            city="TestCity",
        )
        form.save.return_value = order

        cart = MagicMock()
        cart.__iter__.return_value = [
            {
                "product": self.product,
                "quantity": 2,
                "price": str(self.product.price),
                "dimensions": "medium",
                "frame_type": "wooden",
                "frame_color": "black",
            }
        ]
        cart.clear = MagicMock()

        OrderService.create_order_from_cart(form, cart)

        cart.clear.assert_called_once()
        mock_generate_invoice.assert_not_called()
        self.assertEqual(OrderItem.objects.filter(order=order).count(), 1)


    @patch("orders.services.InvoiceService.generate_invoice")
    def test_generates_invoice_when_invoice_pdf_missing(self, mock_generate):
        order = MagicMock()
        order.id = 999
        order.invoice_pdf = None

        OrderService.get_order_invoice(order)
        mock_generate.assert_called_once_with(order)


    @patch("orders.services.InvoiceService.generate_invoice")
    def test_generates_invoice_when_invoice_pdf_exists(self, mock_generate):
        mock_file = MagicMock()
        mock_file.path = "/tmp/fake_invoice.pdf"

        order = MagicMock()
        order.id = 123
        order.invoice_pdf = mock_file

        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value = MagicMock(name="file_obj")

            result = OrderService.get_order_invoice(order)

            mock_open.assert_called_once_with("/tmp/fake_invoice.pdf", "rb")
            mock_generate.assert_not_called()
            self.assertEqual(result, mock_open.return_value)