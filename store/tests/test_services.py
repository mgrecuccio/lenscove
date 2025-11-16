from decimal import Decimal
from django.test import TestCase
from store.models import Product, Category
from store.services import StoreService


class StoreServicesTest(TestCase):
    def setUp(self):
        self.category1 = Category.objects.create(
            name="Landscapes",
            slug="landscapes"
        )

        self.category2 = Category.objects.create(
            name="Portraits",
            slug="portraits"
        )

        self.products = []
        for i in range(6):
            category = self.category1 if i < 3 else self.category2
            self.products.append(
                Product.objects.create(
                    category=category,
                    title=f"Test Product {i+1}",
                    slug=f"test-product-{i+1}",
                    price=Decimal("9.99"),
                    description=f"Description for product {i+1}"
                )
            )


    def test_get_best_sellers_returns_limited_products(self):
        products = StoreService.get_best_sellers()
        self.assertEqual(len(products), 4)

        products = StoreService.get_best_sellers(limit=2)
        self.assertEqual(len(products), 2)


        products = StoreService.get_best_sellers(limit=10)
        self.assertEqual(len(products), 6)

    
    def test_get_products_by_category_with_valid_category(self):
        products = StoreService.get_products_by_category(self.category1.slug)
        self.assertEqual(len(products), 3)
        for product in products:
            self.assertEqual(product.category, self.category1)

        products = StoreService.get_products_by_category(self.category2.slug)
        self.assertEqual(len(products), 3)
        for product in products:
            self.assertEqual(product.category, self.category2)

    
    def test_get_products_by_category_with_invalid_category(self):
        products = StoreService.get_products_by_category("non-existent")
        self.assertEqual(len(products), 0)

    
    def test_get_products_by_category_without_category(self):
        products = StoreService.get_products_by_category()
        self.assertEqual(len(products), 6)

    
    def test_get_product_by_slug_with_valid_slug(self):
        product = StoreService.get_product_by_slug("test-product-1")
        self.assertIsNotNone(product)
        self.assertEqual(product.title, "Test Product 1")


    def test_get_active_categories_returns_all_categories(self):
        categories = StoreService.get_active_categories()
        self.assertEqual(len(categories), 2)
        category_names = {c.name for c in categories}
        self.assertEqual(category_names, {"Landscapes", "Portraits"})

    
    def test_get_product_by_slug_with_invalid_slug(self):
        product = StoreService.get_product_by_slug("non-existent")
        self.assertIsNone(product)


    def tearDown(self):
        for product in self.products:
            if product.image:
                product.image.delete()