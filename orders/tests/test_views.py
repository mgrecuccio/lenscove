from django.test import TestCase
from django.urls import reverse
from orders.models import Order, OrderItem
from store.models import Product
from unittest.mock import patch


class OrderCreateViewsTest(TestCase):


    def setUp(self):
        self.product = Product.objects.create(
            title='test-title',
            brand='test-brand',
            description='test-description',
            slug='test-slug',
            price=10.00
        )

    
    @patch("orders.utils.send_order_confirmation_email")
    def test_order_create_post(self, mock_send_email):
        session = self.client.session
        session["cart"] = {
            str(self.product.id): {
                "quantity": 2,
                "price": str(self.product.price),
                "dimensions": "medium",
                "frame_type": "wooden",
                "frame_color": "black"
            }
        }
        session.save()

        response = self.client.post(reverse("orders:order_create"), {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "address": "123 Test Street",
            "postal_code": "12345",
            "city": "TestCity",
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/order_created.html")

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        order_item = OrderItem.objects.first()
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.product, self.product)
        mock_send_email.called


    def test_order_create_get(self):
        response = self.client.get(reverse("orders:order_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/order_create.html")
        self.assertIn("form", response.context)
        self.assertIn("cart", response.context)