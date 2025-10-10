from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .invoice import generate_invoice


def send_order_confirmation_email(order):
    subject = f'Order Confirmation - Order #{order.id}'
    message = render_to_string("orders/order_email.txt", {"order": order})
    html_message = render_to_string("orders/order_email.html", {"order": order})

    msg = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )
    msg.attach_alternative(html_message, "text/html")

    pdf_buffer = generate_invoice(order)
    pdf_buffer.seek(0)
    msg.attach(f"invoice_{order.id}.pdf", pdf_buffer.read(), "application/pdf")

    msg.send()