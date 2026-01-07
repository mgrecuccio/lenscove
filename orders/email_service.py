from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from orders.models import Order


class EmailService:

    @staticmethod
    def send_order_confirmation_email(order: Order, pdf_buffer=None):
        subject = f"Order Confirmation - Order #{order.id}"

        context = {
            "order": order,
            "brand_logo_url": getattr(settings, "BRAND_LOGO_URL", ""),
            "brand_banner_url": getattr(settings, "BRAND_BANNER_URL", ""),
        }

        message = render_to_string("orders/order_email.txt", context)
        html_message = render_to_string("orders/order_email.html", context)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        msg.attach_alternative(html_message, "text/html")

        invoice = getattr(order, "invoice_pdf", None)

        if invoice:
            try:
                msg.attach_file(invoice.path)
            except Exception:
                invoice.open("rb")
                msg.attach(
                    filename=f"invoice_{order.id}.pdf",
                    content=invoice.read(),
                    mimetype="application/pdf",
                )
                invoice.close()
        
        elif pdf_buffer is not None:
            pdf_buffer.seek(0)
            msg.attach(
                filename=f"invoice_{order.id}.pdf",
                content=pdf_buffer.read(),
                mimetype="application/pdf",
            )

        msg.send()
        order.mark_confirmation_mail_sent_at()