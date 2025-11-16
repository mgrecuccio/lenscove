import logging
from mollie.api.client import Client
from django.db import transaction
from django.conf import settings
from orders.models import Order
from payments.models import Payment

logger = logging.getLogger(__name__)

class PaymentService:
    
    @staticmethod
    def get_mollie_client() -> Client:
        client = Client()
        client.set_api_key(settings.MOLLIE_API_KEY)
        return client
    

    @staticmethod
    @transaction.atomic
    def create_payment(order: Order, request):
        mollie = PaymentService.get_mollie_client()
        webhook_url = settings.MOLLIE_WEBHOOK_URL
        redirect_url = settings.MOLLIE_REDIRECT_URL

        mollie_payment = mollie.payments.create({
            "amount": {"currency": "EUR", "value": f"{order.get_total_cost():.2f}"},
            "description": f"Order #{order.id}",
            "webhookUrl": webhook_url,
            "redirectUrl": redirect_url,
            "metadata": {"order_id": order.id},
        })

        #ensure redirect URL includes payment id
        redirect_with_id = f"{redirect_url}?payment_id={mollie_payment.id}"
        mollie.payments.update(mollie_payment.id, {"redirectUrl": redirect_with_id})

        Payment.objects.create(
            order=order,
            mollie_id=mollie_payment.id,
            amount=order.get_total_cost(),
            status="open",
        )

        logger.info(f"Payment {mollie_payment.id} created for order {order.id}")
        return mollie_payment