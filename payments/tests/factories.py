from unittest.mock import Mock

class FakeMolliePayment:
    def __init__(self, order_id, status="open", redirect_url=None, checkout_url=None):
        self.id = f"tr_{order_id:06d}"
        self.metadata = {"order_id": order_id}
        self.status = status
        self.redirect_url = redirect_url or f"http://localhost:8000/"
        self.checkout_url = checkout_url or f"https://fake-mollie.test/checkout/{self.id}"

    def is_paid(self):
        return self.status == "paid"

    def is_canceled(self):
        return self.status == "canceled"

    def is_expired(self):
        return self.status == "expired"


class FakeMollieClient(Mock):
    def __init__(self):
        super().__init__()
        self._payments = {}

        
        self.payments = Mock()
        def create_payment(data):
            order_id = data["metadata"]["order_id"]
            fake_payment = FakeMolliePayment(order_id, status="open")
            self._payments[fake_payment.id] = fake_payment
            return fake_payment

        def get_payment(payment_id):
            return self._payments.get(payment_id)
        
        def update_payment(payment_id, data):
            payment = self._payments.get(payment_id)
            if not payment:
                return None
            if "redirectUrl" in data:
                payment.redirectUrl = data["redirectUrl"]
            return payment

        self.payments.create.side_effect = create_payment
        self.payments.get.side_effect = get_payment
        self.payments.update.side_effect = update_payment