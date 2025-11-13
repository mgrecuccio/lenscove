from typing import Optional
from django.db.models import QuerySet
from .models import Product, Category


class StoreService:

    @staticmethod
    def get_best_sellers(limit: int = 4) -> QuerySet[Product]:
        return Product.objects.all()[:limit]

    @staticmethod
    def get_products_by_category(category_slug: Optional[str] = None) -> QuerySet[Product]:
        if not category_slug:
            return Product.objects.all()
        
        try:
            category = Category.objects.get(slug=category_slug)
            return Product.objects.filter(category=category)
        except Category.DoesNotExist:
            return Product.objects.none()

    @staticmethod
    def get_product_by_slug(slug: str) -> Product | None:
        try:
            return Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return None

    @staticmethod
    def get_active_categories() -> QuerySet[Category]:
        return Category.objects.all()