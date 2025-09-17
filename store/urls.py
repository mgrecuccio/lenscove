from django.urls import path
from . import views

urlpatterns = [
    path('', views.best_sellers, name='store'),
    path('gallery', views.gallery, name='gallery'),
    path('gallery/<slug:slug>/', views.gallery, name='gallery_by_category'),
    path('product/<slug:slug>/', views.product_details, name='product_details'),
]