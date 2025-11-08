import requests
import shippo
import logging
from shippo.models import components
from django.conf import settings
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

shippo_sdk = shippo.Shippo(api_key_header=settings.SHIPPO_API_KEY)


class ShippingService:

    @staticmethod
    def create_shippo_label(order):
        try:
            shipment = ShippingService._create_shipment(order)
            rate = shipment.rates[0]

            transaction = shippo_sdk.transactions.create(
                components.TransactionCreateRequest(
                    rate=rate.object_id,
                    label_file_type=components.LabelFileType.PDF,
                    async_= False
                )
            )

            if transaction.status != "SUCCESS":
                raise Exception(f"Shippo label creation failed: {transaction.messages}")

            logger.info("Shippo transaction successfully created")

            pdf_bytes = requests.get(transaction.label_url, timeout=30).content
            return {
                "shippo_id": transaction.object_id,
                "tracking_number": transaction.tracking_number,
                "tracking_url": transaction.tracking_url_provider,
                "label_file": ContentFile(pdf_bytes),
            }
        except Exception as e:
            logger.error(f"Error creating Shippo label for order {order.id}: {e}")
            raise

    
    @staticmethod
    def _create_shipment(order):
        address_from = components.AddressCreateRequest(
            name="LensCove Print",
            street1="Rue Servandoni, 45",
            city="San Francisco",
            state="CA",
            zip="94117-1913",
            country="US",
        )
        address_to = components.AddressCreateRequest(
            name=f"{order.first_name} {order.last_name}",
            street1="215 Clayton St",
            city="San Francisco",
            state="CA",
            zip="94117-1913",
            country="US",
            phone="468380255",
            email=order.email,
        )
        parcel = components.ParcelCreateRequest(
            length="30", width="20", height="5",
            distance_unit=components.DistanceUnitEnum.CM,
            weight="0.5", mass_unit=components.WeightUnitEnum.KG
        )

        return shippo_sdk.shipments.create(
            components.ShipmentCreateRequest(
                address_from=address_from,
                address_to=address_to,
                parcels=[parcel],
                async_=False
            )
        )