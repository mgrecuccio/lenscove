from django.test import TestCase
from store.models import Category,Product
from django.db.models.fields import TextField, DecimalField

class CategoryTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Category.objects.create(name='test-category-name', slug='test-category-slug')

    def test_name_label(self):
        category = Category.objects.get(id=1)
        field_label = category._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_max_length(self):
        category = Category.objects.get(id=1)
        max_length = category._meta.get_field('name').max_length
        self.assertEqual(max_length, 250)

    def test_slug_label(self):
        category = Category.objects.get(id=1)
        field_label = category._meta.get_field('slug').verbose_name
        self.assertEqual(field_label, 'slug')

    def test_slug_max_length(self):
        category = Category.objects.get(id=1)
        max_length = category._meta.get_field('slug').max_length
        self.assertEqual(max_length, 250)


class ProductTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Product.objects.create(
            title='test-title',
            brand='test-brand',
            description='test-description',
            slug='test-slug',
            price=9.99
        )

    def test_title_label(self):
        product = Product.objects.get(id=1)
        field_label = product._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_title_max_length(self):
        product = Product.objects.get(id=1)
        max_length = product._meta.get_field('title').max_length
        self.assertEqual(max_length, 250)

    def test_brand_label(self):
        product = Product.objects.get(id=1)
        field_label = product._meta.get_field('brand').verbose_name
        self.assertEqual(field_label, 'brand')

    def test_brand_max_length(self):
        product = Product.objects.get(id=1)
        max_length = product._meta.get_field('brand').max_length
        self.assertEqual(max_length, 150)

    def test_description_label(self):
        product = Product.objects.get(id=1)
        field_label = product._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')

    def test_description_type(self):
        product = Product.objects.get(id=1)
        field = product._meta.get_field('description')
        self.assertTrue(type(field) is TextField)

    def test_slug_label(self):
        product = Product.objects.get(id=1)
        field_label = product._meta.get_field('slug').verbose_name
        self.assertEqual(field_label, 'slug')

    def test_slug_max_length(self):
        product = Product.objects.get(id=1)
        max_length = product._meta.get_field('slug').max_length
        self.assertEqual(max_length, 250)

    def test_price_label(self):
        product = Product.objects.get(id=1)
        field_label = product._meta.get_field('price').verbose_name
        self.assertEqual(field_label, 'price')

    def test_price_type(self):
        product = Product.objects.get(id=1)
        field = product._meta.get_field('price')
        self.assertTrue(type(field) is DecimalField)