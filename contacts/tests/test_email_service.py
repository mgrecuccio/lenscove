from django.test import TestCase, override_settings
from contacts.models import Contact
from unittest.mock import patch
from contacts.email_service import ContactEmailsService
from django.core import mail


@override_settings(CONTACT_RECEIVER_EMAIL='test_contact_admin@example.com')
class ContactsEmailServiceTest(TestCase):

    def setUp(self):
        self.contact = Contact.objects.create(
            first_name = "test-first-name",
            last_name = "test-last-name",
            email = "email@test.com",
            subject = "test-subject",
            message = "test-message",
        )

    
    @patch("contacts.email_service.render_to_string")
    def test_send_autoreply_email(self, mock_render):
        mock_render.side_effect = [
            "plain text body",
            "<p>html body</p>",
        ]

        ContactEmailsService.send_contact_autoreply_email(self.contact)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]

        self.assertIn("Thanks for contacting LensCove", message.subject)
        self.assertIn(self.contact.email, message.to)
        self.assertEqual(len(message.alternatives), 1)
        self.assertEqual(message.alternatives[0][1], "text/html")


    @patch("contacts.email_service.render_to_string")
    def test_send_notification_email(self, mock_render):
        mock_render.side_effect = [
            "plain text body",
            "<p>html body</p>",
        ]

        ContactEmailsService.send_contact_notification_email(self.contact)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]

        self.assertIn("[LensCove Contact] test-subject", message.subject)
        self.assertIn("test_contact_admin@example.com", message.to)
        self.assertEqual(len(message.alternatives), 1)
        self.assertEqual(message.alternatives[0][1], "text/html")