from django.urls import path
from .views import shippo_webhook

urlpatterns = [
    path("webhook/", shippo_webhook, name="shippo_webhook"),
]