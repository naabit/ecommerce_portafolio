from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CheckoutForm
from .models import OrderItem, Product


# =========================
# Catálogo
# =========================

def product_list(request):
    products = Product.objects.select_related("category").all()
    return render(request, "store/product_list.html", {"products": products})


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        pk=pk,
    )
    return render(request, "store/product_detail.html", {"product": product})


# =========================
# Carrito
# =========================

@login_required
@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    cart = request.session.get("cart", {})
    product_id = str(product.pk)

    try:
        current_quantity = int(cart.get(product_id, 0) or 0)
    except (TypeError, ValueError):
        current_quantity = 0

    raw_quantity = request.POST.get("quantity", "1")
    try:
        quantity_to_add = int(raw_quantity)
    except (TypeError, ValueError):
        quantity_to_add = 0

    if quantity_to_add < 1:
        messages.error(request, "Selecciona una cantidad válida.")
        return _safe_redirect_back(request, fallback_url="store:product_list")

    if product.stock < 1:
        messages.warning(request, f'"{product.name}" no tiene stock disponible.')
        return _safe_redirect_back(request, fallback_url="store:product_list")

    available_to_add = max(int(product.stock) - current_quantity, 0)

    if quantity_to_add <= available_to_add:
        cart[product_id] = current_quantity + quantity_to_add
        request.session["cart"] = cart
        request.session.modified = True
        if quantity_to_add == 1:
            messages.success(request, f'"{product.name}" fue agregado correctamente al carrito.')
        else:
            messages.success(
                request,
                f'Se agregaron {quantity_to_add} unidades de "{product.name}" correctamente al carrito.',
            )
    else:
        messages.warning(
            request,
            f'No se pudo agregar "{product.name}". Stock disponible para agregar: {available_to_add}.',
        )

    return _safe_redirect_back(request, fallback_url="store:product_list")


def _safe_redirect_back(request, fallback_url: str):
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)

    return redirect(fallback_url)


@login_required
def cart_detail(request):
    cart = request.session.get("cart", {})
    product_ids = cart.keys()

    products = Product.objects.filter(id__in=product_ids).select_related("category")

    cart_items = []
    total = Decimal("0")

    for product in products:
        try:
            quantity = int(cart.get(str(product.id), 0) or 0)
        except (TypeError, ValueError):
            quantity = 0

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
@require_POST
def update_cart_item(request, pk):
    product = get_object_or_404(Product, pk=pk)

    cart = request.session.get("cart", {})
    product_id = str(product.pk)

    try:
        current_quantity = int(cart.get(product_id, 0) or 0)
    except (TypeError, ValueError):
        current_quantity = 0

    raw_delta = request.POST.get("delta")
    if raw_delta is not None:
        try:
            delta = int(raw_delta)
        except (TypeError, ValueError):
            delta = 0
        new_quantity = current_quantity + delta
    else:
        raw_quantity = request.POST.get("quantity", "")
        try:
            new_quantity = int(raw_quantity)
        except (TypeError, ValueError):
            new_quantity = -1

    if new_quantity < 1:
        if product_id in cart:
            del cart[product_id]
            request.session["cart"] = cart
            request.session.modified = True
            messages.info(request, f'"{product.name}" fue eliminado del carrito.')
        return redirect("store:cart_detail")

    if product.stock < new_quantity:
        messages.warning(
            request,
            f'No se pudo actualizar "{product.name}". Stock disponible: {int(product.stock)}.',
        )
        return redirect("store:cart_detail")

    cart[product_id] = new_quantity
    request.session["cart"] = cart
    request.session.modified = True
    messages.success(request, f'"{product.name}" se actualizó correctamente.')

    return redirect("store:cart_detail")


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


# =========================
# Checkout
# =========================

@login_required
def checkout(request):
    cart = request.session.get("cart", {})

    if not cart:
        messages.warning(request, "Tu carrito está vacío.")
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

                if product.stock < quantity:
                    form.add_error(None, f"No hay suficiente stock para {product.name}.")
                    order.delete()
                    context = {
                        "form": form,
                        "cart_items": cart_items,
                        "total": total,
                    }
                    return render(request, "store/checkout.html", context)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=quantity,
                )

                product.stock -= quantity
                product.save()

            request.session["cart"] = {}
            request.session.modified = True
            messages.success(request, "Compra realizada correctamente.")

            return redirect("store:checkout_success", order_id=order.id)
    else:
        form = CheckoutForm()

    context = {
        "form": form,
        "cart_items": cart_items,
        "total": total,
    }
    return render(request, "store/checkout.html", context)


# =========================
# Confirmación
# =========================

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
