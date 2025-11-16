import logging
from orders.models import Order
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .services import PaymentService
from .webhook_service import WebhookService


logger = logging.getLogger(__name__)


def create_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, paid=False)
    mollie_payment = PaymentService.create_payment(order, request)
    return redirect(mollie_payment.checkout_url)


@csrf_exempt
def mollie_webhook(request):
    payment_id = request.POST.get("id")

    if not payment_id:
        return HttpResponse("Missing payment ID", status=400)

    mollie = PaymentService.get_mollie_client()
    payment_data = mollie.payments.get(payment_id)

    WebhookService.process(payment_data)
    return HttpResponse("Webhook received", 200)


def payment_return(request):
    logger.info(f"Mollie Webhook called with request GET params: {request.GET}")
    
    payment_id = request.GET.get("payment_id")
    if not payment_id:
        logger.warning("Missing payment ID in redirect.")
        return HttpResponse("Missing payment ID", status=400)

    mollie = PaymentService.get_mollie_client()
    payment_data = mollie.payments.get(payment_id)
    order_id = payment_data.metadata.get("order_id")
    order = get_object_or_404(Order, id=order_id)

    template = "orders/order_created.html" if order.paid else "payments/payment_pending.html"
    return render(request, template, {"order": order})
