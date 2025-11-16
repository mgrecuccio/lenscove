import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .webhook_service import WebhookService

logger = logging.getLogger(__name__)


@csrf_exempt
def shippo_webhook(request) -> HttpResponse:
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Shippo webhook")
        return HttpResponse(status=400)
    
    status_code = WebhookService.handle_shippo_webhook(data)
    return HttpResponse(status=status_code)
