from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from orders.email_service import EmailService
from django.core import mail


@override_settings(DEFAULT_FROM_EMAIL='test_sender@example.com')
class SendOrderEmailTests(TestCase):

    def setUp(self):
        self.order = MagicMock()
        self.order.id = 42
        self.order.email = "john.doe@example.com"
        self.order.invoice_pdf = None

    
    @patch("orders.email_service.render_to_string")
    def test_send_email_with_generated_pdf_attachment(self, mock_render):
        mock_render.side_effect = [
            "plain text body",
            "<p>html body</p>",
        ]

        fake_pdf = MagicMock()
        fake_pdf.read.return_value = b"fake-pdf-data"
        EmailService.send_order_confirmation_email(self.order, fake_pdf)


        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertIn("Order Confirmation", message.subject)
        self.assertIn(self.order.email, message.to)
        self.assertEqual(len(message.alternatives), 1)
        self.assertEqual(message.alternatives[0][1], "text/html")

        attachment_name, attachment_content, attachment_type = message.attachments[0]
        self.assertTrue(attachment_name.startswith("invoice_"))
        self.assertEqual(attachment_type, "application/pdf")
        self.assertEqual(attachment_content, b"fake-pdf-data")


    @patch("orders.email_service.render_to_string")
    def test_send_email_uses_existing_pdf_file(self, mock_render):
        mock_render.side_effect = [
            "plain text body",
            "<p>html body</p>",
        ]
        mock_file = MagicMock()
        mock_file.path = "/tmp/invoice_42.pdf"
        self.order.invoice_pdf = mock_file

        with patch("orders.email_service.EmailMultiAlternatives.attach_file") as mock_attach:
            EmailService.send_order_confirmation_email(self.order, MagicMock())
            mock_attach.assert_called_once_with("/tmp/invoice_42.pdf")
                