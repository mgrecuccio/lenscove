import io
import os
from django.conf import settings
from django.test import TestCase, RequestFactory
from django.http import Http404
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from store.views import categories, product_details
from store.models import Product, Category, ImageDimension, FrameType, FrameColor

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


class StoreViewsTestCase(TestCase):

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
        self.factory = RequestFactory()
        
        self.category = Category.objects.create(name='Test Category')

        self.product1 = Product.objects.create(
            title='Product-1',
            brand='test-brand',
            description='test-description',
            slug='product-1',
            price=9.99,
            image=get_test_image()
        )
        self.product2 = Product.objects.create(
            title='Product-2',
            brand='test-brand',
            description='test-description',
            slug='product-2',
            price=9.99,
            image=get_test_image()
        )
        self.product3 = Product.objects.create(
            title='Product-3',
            brand='test-brand',
            description='test-description',
            slug='product-3',
            price=9.99,
            image=get_test_image()
        )
        self.product4 = Product.objects.create(
            title='Product-4',
            brand='test-brand',
            description='test-description',
            slug='product-4',
            price=9.99,
            image=get_test_image()
        )
        self.product5 = Product.objects.create(
            title='Product-5',
            brand='test-brand',
            description='test-description',
            slug='product-5',
            price=9.99,
            image=get_test_image()
        )


    def test_categories_view(self):
        request = self.factory.get('/categories/')
        response_data = categories(request)
        self.assertIn(self.category, response_data['all_categories'])
        self.assertEqual(len(response_data['all_categories']), 1)


    def test_best_sellers_view(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'store/store.html')
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn('best_sellers', context)
        self.assertEqual(len(context['best_sellers']), 4)
        self.assertEqual(list(context['best_sellers']), [self.product1, self.product2, self.product3, self.product4])


    def test_gallery_view(self):
        response = self.client.get('/gallery')
        self.assertTemplateUsed(response, 'store/gallery.html')
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn('all_products', context)
        self.assertEqual(len(context['all_products']), 5)

    
    @patch('django.shortcuts.get_object_or_404')
    def test_product_details_view(self, mock_get):
        mock_get.return_value = self.product1
        response = self.client.get('/product/product-1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product-details.html')

        self.assertEqual(response.context['product'], self.product1)
        self.assertEqual(response.context['image_dimensions'], ImageDimension)
        self.assertEqual(response.context['frame_types'], FrameType)
        self.assertEqual(response.context['frame_colors'], FrameColor)


    @patch('django.shortcuts.get_object_or_404')
    def test_product_details_not_found(self, mock_get):
        mock_get.side_effect = Http404("No Product matches the given query.")
        request = self.factory.get('/product/non-existent/')
        with self.assertRaises(Http404):
            product_details(request, slug='non-existent')