from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CheckoutForm
from .models import OrderItem, Product


def home(request):
    return render(request, "store/home.html")


def product_list(request):
    products = Product.objects.select_related("category").all()
    return render(request, "store/product_list.html", {"products": products})


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        pk=pk
    )
    return render(request, "store/product_detail.html", {"product": product})

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    cart = request.session.get("cart", {})
    product_id = str(product.pk)

    current_quantity = cart.get(product_id, 0)

    if current_quantity < product.stock:
        cart[product_id] = current_quantity + 1
        request.session["cart"] = cart
        request.session.modified = True
        messages.success(request, f'"{product.name}" fue agregado al carrito.')
    else:
        messages.warning(
            request,
            f'No puedes agregar más unidades de "{product.name}" porque supera el stock disponible.'
        )

    return redirect("store:cart_detail")

@login_required
def cart_detail(request):
    cart = request.session.get("cart", {})
    product_ids = cart.keys()

    products = Product.objects.filter(id__in=product_ids).select_related("category")

    cart_items = []
    total = Decimal("0")

    for product in products:
        quantity = cart.get(str(product.id), 0)
        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    context = {
        "cart_items": cart_items,
        "total": total,
    }
    return render(request, "store/cart_detail.html", context)

@login_required
def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    cart = request.session.get("cart", {})
    product_id = str(product.pk)

    if product_id in cart:
        del cart[product_id]
        request.session["cart"] = cart
        request.session.modified = True
        messages.info(request, f'"{product.name}" fue eliminado del carrito.')

    return redirect("store:cart_detail")

@login_required
def checkout(request):
    cart = request.session.get("cart", {})

    if not cart:
        return redirect("store:cart_detail")

    cart_items = []
    total = Decimal("0")

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        quantity = int(quantity)
        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            for item in cart_items:
                product = item["product"]
                quantity = item["quantity"]

                # Validar stock suficiente
                if product.stock < quantity:
                    form.add_error(None, f"No hay suficiente stock para {product.name}.")
                    order.delete()
                    return render(request, "store/checkout.html", {
                        "form": form,
                        "cart_items": cart_items,
                        "total": total,
                    })

                # Crear item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=quantity,
                )

                # Descontar stock
                product.stock -= quantity
                product.save()

            request.session["cart"] = {}
            request.session.modified = True

            return redirect("store:checkout_success", order_id=order.id)
    else:
        form = CheckoutForm()

    context = {
        "form": form,
        "cart_items": cart_items,
        "total": total,
    }
    return render(request, "store/checkout.html", context)

@login_required
def checkout_success(request, order_id):
    order = get_object_or_404(
        request.user.orders.prefetch_related("items__product"),
        pk=order_id,
    )

    context = {
        "order": order,
    }
    return render(request, "store/checkout_success.html", context)
