import logging
from orders.models import Order
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Payment
from payments.services import create_mollie_payment, get_mollie_client


logger = logging.getLogger(__name__)


def create_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, paid=False)

    mollie_payment = create_mollie_payment(order, request)

    Payment.objects.create(
        order=order,
        mollie_id=mollie_payment.id,
        amount=order.get_total_cost(),
        status="open",
    )

    logger.info(f"Created Mollie payment {mollie_payment.id} for order {order.id}")
    return redirect(mollie_payment.checkout_url)


@csrf_exempt
def mollie_webhook(request):
    payment_id = request.POST.get("id")

    if not payment_id:
        return HttpResponse("Missing payment ID", status=400)

    mollie = get_mollie_client()
    payment_data = mollie.payments.get(payment_id)

    order_id = payment_data.metadata.get("order_id")
    order = get_object_or_404(Order, id=order_id)
    payment = Payment.objects.get(order=order)

    logger.info(f"Webhook received for order {order_id} with status {payment_data.status}")

    if payment_data.is_paid() and not order.paid:
        _handle_successful_payment(order, payment)
        return HttpResponse("Webhook received", status=200)

    if payment_data.status in ["canceled", "expired", "failed"]:
        payment.mark_failed(payment_data.status)
        logger.warning(f"Payment {payment_id} failed ({payment_data.status}) for order {order.id}")
        return render(
            request,
            "payments/payment_failed.html",
            {"order": order, "status": payment_data.status}
        )

    return render(
        request,
        "payments/payment_pending.html",
        {"order": order}
    )


def payment_return(request):
    logger.info("Mollie returned to site.")
    logger.info(f"Request GET params: {request.GET}")
    mollie = get_mollie_client()

    payment_id = request.GET.get("payment_id")
    if not payment_id:
        logger.warning("Missing payment ID in redirect.")
        return HttpResponse("Missing payment ID", status=400)

    payment_data = mollie.payments.get(payment_id)
    order_id = payment_data.metadata.get("order_id")
    order = get_object_or_404(Order, id=order_id)

    if order.paid:
        logger.info(f"Payment successful for order id = {order.id}")
        return render(request, "orders/order_created.html", {"order": order})
    else:
        logger.info(f"Payment still pending for order id = {order.id}")
        return render(request, "payments/payment_pending.html", {"order": order})


def _handle_successful_payment(order: Order, payment: Payment) -> None:
    logger.info(f"Order {order.id} paid successfully.")
    payment.mark_paid()
    order.mark_paid()

    try:
        from orders.utils import send_order_confirmation_email, generate_invoice
        from django.core.files.base import ContentFile

        pdf_buffer = generate_invoice(order)
        pdf_buffer.seek(0)
        order.invoice_pdf.save(
            f"invoice_{order.id}.pdf",
            ContentFile(pdf_buffer.read()),
            save=True,
        )
        send_order_confirmation_email(order)
        logger.info(f"Order {order.id} invoice saved and confirmation email sent.")
    except Exception as exc:
        logger.exception(f"Failed to generate/send invoice for order {order.id}: {exc}")

    try:
        _create_shipment_and_label(order)
    except Exception as exc:
        logger.exception(f"Shipment creation failed for order {order.id}: {exc}")


def _create_shipment_and_label(order: Order) -> None:
    from shipping.models import Shipment
    from shipping.services import create_shippo_label

    shipment = Shipment.objects.create(order=order)
    try:
        label_info = create_shippo_label(order)
        shipment.mark_label_created(
            shippo_id=label_info["shippo_id"],
            tracking_number=label_info["tracking_number"],
            tracking_url=label_info["tracking_url"],
            label_file=label_info["label_file"],
        )
        logger.info(f"Shipment label created for order {order.id}")
    except Exception as e:
        shipment.update_status("error")
        logger.error(f"Failed to create label for order {order.id}: {e}")