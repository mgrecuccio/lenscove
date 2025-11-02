import logging
from mollie.api.client import Client
from django.conf import settings

logger = logging.getLogger(__name__)


def get_mollie_client():
    client = Client()
    client.set_api_key(settings.MOLLIE_API_KEY)
    return client


def create_mollie_payment(order, request):
    mollie = get_mollie_client()

    base_redirect_url = settings.MOLLIE_REDIRECT_URL
    webhook_url = settings.MOLLIE_WEBHOOK_URL

    payment = mollie.payments.create({
        "amount": {
            "currency": "EUR",
            "value": f"{order.get_total_cost():.2f}",
        },
        "description": f"Order #{order.id}",
        "webhookUrl": webhook_url,
        "redirectUrl": base_redirect_url,
        "metadata": {
            "order_id": order.id,
        },
    })

    # Update the payment_redirect_url because Mollie not always calls
    # the payment return url with the payment id as a query parameter
    payment_redirect_url = f"{base_redirect_url}?payment_id={payment.id}"
    payment = mollie.payments.update(payment.id, {"redirectUrl": payment_redirect_url})

    return payment
