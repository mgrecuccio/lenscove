import logging
from django.http import HttpResponse
from django.db import transaction
from django.core.mail import send_mail
from .models import Shipment

logger = logging.getLogger(__name__)


class WebhookService:

    @staticmethod
    @transaction.atomic
    def handle_shippo_webhook(payload: dict) -> int:
        event = payload.get("event")
        tracking_number = payload.get("data", {}).get("tracking_number")
        new_status = payload.get("data", {}).get("tracking_status", {}).get("status")

        logger.info(f"Received Shippo event '{event}' for tracking_number={tracking_number}")

        if not tracking_number:
            logger.warning("No tracking number in webhook payload")
            return 400
        
        try:
            shipment = Shipment.objects.get(tracking_number=tracking_number)
        except Shipment.DoesNotExist:
            logger.warning(f"Unknowk shipment with tracking number {tracking_number}")
            return 404
        

        if not new_status:
            logger.info(f"No new status found for shipment {shipment.id}")
            return 200
        
        shipment.update_status(new_status)
        logger.info(f"Shipment {shipment.id} updated to {new_status}")

        WebhookService._notify_customer(shipment, new_status)
        return 200
    

    @staticmethod
    def _notify_customer(shipment, new_status: str):
        try:
            send_mail(
                subject=f"Your LensCove order is now {new_status}",
                message=f"Your order #{shipment.order.id} is currently {new_status}. "
                        f"Track it here: {shipment.tracking_url}",
                from_email="support@lenscove.com",
                recipient_list=[shipment.order.email],
                fail_silently=True,
            )
            logger.info(f"Notification email sent for shipment {shipment.id}")
        except Exception as e:
            logger.error(f"Failed to send email for shipment {shipment.id}: {e}")