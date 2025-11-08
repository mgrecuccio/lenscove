from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings
from orders.invoice_service import generate_invoice


class GenerateInvoiceTest(TestCase):
    @patch("orders.invoice_service.canvas.Canvas")
    @patch("orders.invoice_service.Image.open")
    @patch("orders.invoice_service.os.path.join")
    def test_generate_invoice_returns_buffer(self, mock_join, mock_open, mock_canvas):
        mock_open.return_value = MagicMock()
        fake_canvas = MagicMock()
        mock_canvas.return_value = fake_canvas
        order = MagicMock()
        order.id = 99
        order.items.all.return_value = []

        buffer = generate_invoice(order)

        self.assertTrue(hasattr(buffer, "read"))
        fake_canvas.drawString.assert_any_call(50, mock_canvas.call_args[1].get("pagesize", (0, 0))[1] - 165, f"Invoice #{order.id}")
        fake_canvas.save.assert_called_once()
        mock_join.assert_called_once_with(settings.BASE_DIR, settings.SHOP_LOGO)


    def test_generate_invoice_handles_missing_logo_gracefully(self):
        order = MagicMock()
        order.id = 1
        order.items.all.return_value = []
        buffer = generate_invoice(order)
        content = buffer.read(20)
        self.assertIsInstance(content, bytes)
