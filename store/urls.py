from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    # catálogo
    path("", views.product_list, name="product_list"),
    path("producto/<int:pk>/", views.product_detail, name="product_detail"),

    # carrito
    path("carrito/", views.cart_detail, name="cart_detail"),
    path("carrito/agregar/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("carrito/quitar/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),

    # checkout
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/exito/", views.checkout_success, name="checkout_success"),
]