from django.test import TestCase
from contacts.models import Contact
from django.db.models.fields import TextField, EmailField, CharField

class ContactTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Contact.objects.create(
            first_name = "test-first-name",
            last_name = "test-last-name",
            email = "email@test.com",
            subject = "test-subject",
            message = "test-message",
        )


    def test_first_name_label(self):
        contact = Contact.objects.get(id=1)
        field_label = contact._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')


    def test_first_name_max_length(self):
        contact = Contact.objects.get(id=1)
        max_length = contact._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 50)


    def test_first_name_field_type(self):
        contact = Contact.objects.get(id=1)
        first_name_field = contact._meta.get_field('first_name')
        self.assertTrue(type(first_name_field) is CharField)

    
    def test_last_name_label(self):
        contact = Contact.objects.get(id=1)
        field_label = contact._meta.get_field('last_name').verbose_name
        self.assertEqual(field_label, 'last name')


    def test_last_name_max_length(self):
        contact = Contact.objects.get(id=1)
        max_length = contact._meta.get_field('last_name').max_length
        self.assertEqual(max_length, 50)


    def test_last_name_field_type(self):
        contact = Contact.objects.get(id=1)
        last_name_field = contact._meta.get_field('last_name')
        self.assertTrue(type(last_name_field) is CharField)

        
    def test_email_field_type(self):
        contact = Contact.objects.get(id=1)
        email_field = contact._meta.get_field('email')
        self.assertTrue(type(email_field) is EmailField)

    
    def test_subject_label(self):
        contact = Contact.objects.get(id=1)
        field_label = contact._meta.get_field('subject').verbose_name
        self.assertEqual(field_label, 'subject')


    def test_subject_max_length(self):
        contact = Contact.objects.get(id=1)
        max_length = contact._meta.get_field('subject').max_length
        self.assertEqual(max_length, 200)


    def test_subject_field_type(self):
        contact = Contact.objects.get(id=1)
        subject_field = contact._meta.get_field('subject')
        self.assertTrue(type(subject_field) is CharField)


    def test_message_label(self):
        contact = Contact.objects.get(id=1)
        field_label = contact._meta.get_field('message').verbose_name
        self.assertEqual(field_label, 'message')


    def test_message_field_type(self):
        contact = Contact.objects.get(id=1)
        message = contact._meta.get_field('message')
        self.assertTrue(type(message) is TextField)