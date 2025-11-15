from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class ContactEmailsService:

    @staticmethod
    def send_contact_notification_email(contact):
        subject = f"[LensCove Contact] {contact.subject}"
        context = {"contact": contact}

        text_body = render_to_string("contacts/contact_notification.txt", context)
        html_body = render_to_string("contacts/contact_notification.html", context)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_RECEIVER_EMAIL],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()


    @staticmethod
    def send_contact_autoreply_email(contact):
        subject = "Thanks for contacting LensCove"
        context = {"contact": contact}

        text_body = render_to_string("contacts/contact_autoreply.txt", context)
        html_body = render_to_string("contacts/contact_autoreply.html", context)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[contact.email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
