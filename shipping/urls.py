from django.urls import path
from .views import shippo_webhook

app_name = 'shipping'

urlpatterns = [
    path("webhook/", shippo_webhook, name="shippo_webhook"),
]