from django.urls import path
from . import views

urlpatterns = [

    path('', view=views.cart_summary, name='cart-summary'),
    path('/add', view=views.cart_add, name='cart-add'),
    path('/delete', view=views.cart_delete, name='cart-delete'),
    path('/update', view=views.cart_update, name='cart-update'),

]