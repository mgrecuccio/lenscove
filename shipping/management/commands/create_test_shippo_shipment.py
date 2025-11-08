import random
from django.core.management.base import BaseCommand, CommandError
from orders.models import Order
from shipping.models import Shipment


class Command(BaseCommand):

    help = "Create a fake shipment linked to a random paid order for Shippo webhook testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "tracking_number",
            type=str,
            nargs="?",
            default="SHIPPO_DELIVERED",
            help="Tracking number to assign to the fake shipment (e.g. SHIPPO_DELIVERED, SHIPPO_TRANSIT)"
        )
        
    
    def handle(self, *args, **options):
        tracking_number = options["tracking_number"]

        order = (
            Order.objects.filter(paid=True).order_by("?").first()
            or Order.objects.create(
                first_name="Test",
                last_name="Customer",
                email="test@example.com",
                address="Test Street 1",
                city="Brussels",
                paid=True,
            )
        )

        shipment = Shipment.objects.filter(tracking_number=tracking_number).first()
        if not shipment:
            shipment = Shipment.objects.create(
                order=order,
                tracking_number=tracking_number,
                tracking_url=f"http://goshippo.com/track/{tracking_number}",
                status="preparation",
            )

        self.stdout.write(self.style.SUCCESS(
            f"Created test shipment #{shipment.id} for order #{order.id}\n"
            f"Tracking number: {tracking_number}\n"
            f"Track URL: {shipment.tracking_url}"
        ))