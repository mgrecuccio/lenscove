import json
import logging
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Shipment

logger = logging.getLogger(__name__)


import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.mail import send_mail
from .models import Shipment

logger = logging.getLogger(__name__)


@csrf_exempt
def shippo_webhook(request) -> HttpResponse:
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception as e:
        logger.error(f"Invalid JSON: {e}")
        return HttpResponse(status=400)

    event = data.get("event")
    test_mode = data.get("test")
    tracking_number = data.get("data", {}).get("tracking_number")
    new_status = data.get("data", {}).get("tracking_status", {}).get("status")

    logger.info(f"Received Shippo event {event} for tracking_number={tracking_number}. Testing mode: {test_mode}")

    if not tracking_number:
        logger.warning("No tracking_number in webhook payload")
        return HttpResponse(status=400)

    try:
        shipment = Shipment.objects.get(tracking_number=tracking_number)
    except Shipment.DoesNotExist:
        logger.warning(f"Unknown shipment for tracking_number={tracking_number}")
        return HttpResponse(status=404)

    if new_status:
        shipment.update_status(new_status)
        logger.info(f"Shipment {shipment.id} updated to {new_status}")

        send_mail(
            subject=f"Your LensCove order is now {new_status}",
            message=f"Your order #{shipment.order.id} is currently {new_status}. "
                    f"Track it here: {shipment.tracking_url}",
            from_email="support@lenscove.com",
            recipient_list=[shipment.order.email],
            fail_silently=True,
        )

    return HttpResponse(status=200)
