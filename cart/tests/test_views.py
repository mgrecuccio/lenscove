import io
import os
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from store.models import Product
from django.conf import settings


def get_test_image():
    image = Image.new('RGB', (100, 100), color='blue')
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    return SimpleUploadedFile(
        'test_image.png',
        image_bytes.read(),
        content_type='image/png'
    )


class CartViewsTest(TestCase):

    def tearDown(self):
        media_root = settings.MEDIA_ROOT
        images_dir = os.path.join(media_root, 'images')
        if os.path.exists(images_dir):
            for filename in os.listdir(images_dir):
                if filename.startswith('test'):
                    file_path = os.path.join(images_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")

        super().tearDown()

    def setUp(self):
        self.product = Product.objects.create(
            title="Test Product",
            slug="test-product",
            price=12.50,
            brand="Test Brand",
            image=get_test_image()
        )

    def test_cart_detail_view(self):
        url = reverse("cart:cart_detail")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cart/detail.html")
        self.assertIn("cart", response.context)


    @patch("cart.views.CartService.add_product_to_cart")
    def test_cart_add_post_valid(self, mock_add_product_to_cart):
        url = reverse("cart:cart_add", args=[self.product.id])
        data = {
            "quantity": 2,
            "dimensions": "normal",
            "frame_type": "plastic",
            "frame_color": "black",
        }
        response = self.client.post(url, data)

        self.assertRedirects(response, reverse("cart:cart_detail"))

        mock_add_product_to_cart.assert_called_once()
        kwargs = mock_add_product_to_cart.call_args.kwargs
        self.assertEqual(kwargs["quantity"], 2)
        self.assertFalse(kwargs["override_quantity"])
        self.assertEqual(kwargs["dimensions"], "normal")
        self.assertEqual(kwargs["frame_type"], "plastic")
        self.assertEqual(kwargs["frame_color"], "black")
        self.assertEqual(kwargs["product"].id, self.product.id)
        self.assertIsNotNone(kwargs["cart"])


    @patch("cart.views.CartService.update_cart_quantity")
    def test_cart_update_quantity_calls_service_with_value(self, mock_update):
        self.add_session_cart()

        url = reverse("cart:cart_update", args=[self.product.id])
        response = self.client.post(url, {"quantity": 3})

        self.assertRedirects(response, reverse("cart:cart_detail"))
        mock_update.assert_called_once()
        args, kwargs = mock_update.call_args
        self.assertEqual(args[1].id, self.product.id)
        self.assertEqual(args[2], "3")


    def add_session_cart(self):
        session = self.client.session
        session['cart'] = {
            str(self.product.id): {
                "title": self.product.title,
                "price": str(self.product.price),
                "image": self.product.image.url,
                'slug': self.product.slug,
                "brand": self.product.brand,
                "quantity": 1,
                "dimensions": "normal",
                "frame_type": "plastic",
                "frame_color": "black"
            }
        }
        session.save()


    @patch("cart.views.CartService.update_cart_quantity")
    def test_cart_update_when_product_not_in_cart_does_not_call_service(self, mock_update):
        url = reverse("cart:cart_update", args=[self.product.id])
        response = self.client.post(url, {"quantity": 2})

        self.assertRedirects(response, reverse("cart:cart_detail"))
        mock_update.assert_not_called()


    @patch("cart.views.CartService.update_cart_quantity")
    def test_cart_update_remove_zero_calls_service(self, mock_update):
        self.add_session_cart()
        url = reverse("cart:cart_update", args=[self.product.id])
        response = self.client.post(url, {"quantity": 0})

        self.assertRedirects(response, reverse("cart:cart_detail"))
        mock_update.assert_called_once()


    @patch("cart.views.CartService.update_cart_quantity")
    def test_cart_update_invalid_quantity_still_calls_service_with_raw_value(self, mock_update):
        self.add_session_cart()
        url = reverse("cart:cart_update", args=[self.product.id])
        response = self.client.post(url, {"quantity": "notanumber"})

        self.assertRedirects(response, reverse("cart:cart_detail"))
        args, kwargs = mock_update.call_args
        self.assertEqual(args[2], "notanumber")

    
    def test_cart_remove_view(self):
        add_url = reverse("cart:cart_add", args=[self.product.id])

        self.client.post(add_url, {
            "quantity": 1,
            "dimensions": "normal",
            "frame_type": "plastic",
            "frame_color": "black",
        })

        remove_url = reverse("cart:cart_remove", args=[self.product.id])
        response = self.client.post(remove_url)

        self.assertRedirects(response, reverse("cart:cart_detail"))

        session = self.client.session
        cart = session.get("cart", session.get(settings.CART_SESSION_ID))
        self.assertFalse(cart)