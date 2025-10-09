from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail


def send_order_confirmation_email(order):
    subject = f'Order Confirmation - Order #{order.id}'
    message = render_to_string("orders/order_email.txt", {"order": order})
    html_message = render_to_string("orders/order_email.html", {"order": order})

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        html_message=html_message,
    )