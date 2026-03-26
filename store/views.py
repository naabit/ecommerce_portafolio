from django.shortcuts import render
from .models import Product


def home(request):
    return render(request, "store/home.html")


def product_list(request):
    products = Product.objects.select_related("category").all().order_by("name")
    return render(request, "store/product_list.html", {"products": products})