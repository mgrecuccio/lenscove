import logging
from django.db import transaction
from orders.models import Order
from payments.models import Payment
from shipping.models import Shipment
from orders.email_service import send_order_confirmation_email
from orders.invoice_service import generate_invoice
from shipping.services import ShippingService
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

class WebhookService:

    @staticmethod
    @transaction.atomic
    def process(payment_data):
        order_id = payment_data.metadata.get("order_id")
        order = Order.objects.select_for_update().get(id=order_id)
        payment = Payment.objects.get(order=order)

        logger.info(f"Processing webhook for order {order_id} with status {payment_data.status}")

        if payment_data.is_paid() and not order.paid:
            WebhookService._mark_paid(order, payment)
        elif payment_data.status in ["canceled", "expired", "failed"]:
            payment.mark_failed(payment_data.status)
        else:
            logger.info(f"Payment {payment_data.id} still pending for order {order.id}")


    @staticmethod
    def _mark_paid(order, payment):
        payment.mark_paid()
        order.mark_paid()
        logger.info(f"Order {order.id} marked as paid")

        pdf_buffer = generate_invoice(order)
        pdf_buffer.seek(0)
        order.invoice_pdf.save(
            f"invoice_{order.id}.pdf",
            ContentFile(pdf_buffer.read()),
            save=True,
        )
        send_order_confirmation_email(order, pdf_buffer)
        logger.info(f"Invoice created and confirmation sent for order {order.id}")

        shipment = Shipment.objects.create(order=order)

        try:
            label_info = ShippingService.create_shippo_label(order)
            shipment.mark_label_created(
                shippo_id=label_info["shippo_id"],
                tracking_number=label_info["tracking_number"],
                tracking_url=label_info["tracking_url"],
                label_file=label_info["label_file"],
            )
            logger.info(f"Shippo label successully created for shippo_id = {shipment.shippo_id}")
        except Exception as exc:
            shipment.update_status("error")
            logger.exception(f"Shipment creation failed for order {order.id}: {exc}")
