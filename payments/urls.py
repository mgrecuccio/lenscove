from django.urls import path
from .views import create_payment, mollie_webhook, payment_return

app_name = 'payments'

urlpatterns = [
    path("create/<int:order_id>/", create_payment, name="create_payment"),
    path("webhook/", mollie_webhook, name="mollie_webhook"),
    path("return/", payment_return, name="payment_return"),
]