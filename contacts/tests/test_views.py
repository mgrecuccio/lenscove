from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from contacts.models import Contact
from contacts.forms import ContactForm


class ContactViewsTest(TestCase):
        
    def test_contact_view_get(self):
        response = self.client.get(reverse("contacts:contact_view"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contacts/contact.html")
        self.assertIn("form", response.context)
        self.assertIn("success", response.context)


    @patch("contacts.views.ContactEmailsService.send_contact_notification_email")
    @patch("contacts.views.ContactEmailsService.send_contact_autoreply_email")
    def test_contact_view_post_valid(self, mock_autoreplay, mock_notify):
        url = reverse("contacts:contact_view")

        data = {
            "first_name": "Marco",
            "last_name": "Rossi",
            "email": "marco@example.com",
            "subject": "Hello",
            "message": "This is a test."
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["success"])

        self.assertEqual(Contact.objects.count(), 1)
        contact = Contact.objects.first()
        self.assertEqual(contact.email, "marco@example.com")

        mock_autoreplay.assert_called_once_with(contact)
        mock_notify.assert_called_once_with(contact)

        self.assertIsInstance(response.context["form"], ContactForm)
        self.assertEqual(response.context["form"].data, {})


    @patch("contacts.views.ContactEmailsService.send_contact_notification_email")
    @patch("contacts.views.ContactEmailsService.send_contact_autoreply_email")
    def test_contact_view_post_invalid(self, mock_autoreply, mock_notify):
        url = reverse("contacts:contact_view")

        data = {
            "first_name": "",
            "last_name": "",
            "email": "not-an-email",
            "subject": "",
            "message": ""
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertFalse(form.is_valid())


        self.assertEqual(Contact.objects.count(), 0)

        mock_notify.assert_not_called()
        mock_autoreply.assert_not_called()

        self.assertFalse(response.context["success"])
