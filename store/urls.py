from django.urls import path
from . import views

urlpatterns = [
    path('', views.best_sellers, name='store'),
    path('gallery', views.gallery, name='gallery'),
    path('product/<slug:slug>/', views.product_details, name='product_details'),
    
]