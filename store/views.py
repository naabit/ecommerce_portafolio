"""
Vistas de la app `store`.

Incluye:
- Catalogo (lista/detalle).
- Carrito basado en sesion.
- Checkout + confirmacion, persistiendo ordenes en DB.

Estructura del carrito en sesion:
    request.session["cart"] = {"<product_id>": <quantity>, ...}
"""

from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CheckoutForm
from .models import Category, OrderItem, Product


# =========================
# Catálogo
# =========================

def product_list(request):
    # Solo mostramos productos activos en el catálogo público.
    products = Product.objects.select_related("category").filter(is_active=True)

    categories = (
        Category.objects.filter(products__is_active=True)
        .distinct()
        .order_by("name")
    )

    raw_q = (request.GET.get("q") or "").strip()
    raw_category = (request.GET.get("category") or "").strip()
    raw_min_price = (request.GET.get("min_price") or "").strip()
    raw_max_price = (request.GET.get("max_price") or "").strip()
    raw_sort = (request.GET.get("sort") or "").strip()
    raw_in_stock = (request.GET.get("in_stock") or "").strip()

    filters = {
        "q": raw_q,
        "category": None,
        "min_price": raw_min_price,
        "max_price": raw_max_price,
        "sort": raw_sort,
        "in_stock": raw_in_stock.lower() in {"1", "true", "on", "yes"},
    }

    if raw_q:
        products = products.filter(
            Q(name__icontains=raw_q)
            | Q(description__icontains=raw_q)
            | Q(category__name__icontains=raw_q)
        )

    if raw_category:
        try:
            filters["category"] = int(raw_category)
            products = products.filter(category_id=filters["category"])
        except (TypeError, ValueError):
            filters["category"] = None

    def _parse_price(raw_value: str):
        try:
            value = Decimal(raw_value)
        except (InvalidOperation, TypeError, ValueError):
            return None
        if value < 0:
            return None
        return value

    min_price = _parse_price(raw_min_price) if raw_min_price else None
    max_price = _parse_price(raw_max_price) if raw_max_price else None
    if min_price is not None and max_price is not None and min_price > max_price:
        min_price, max_price = max_price, min_price

    if min_price is not None:
        products = products.filter(price__gte=min_price)
    if max_price is not None:
        products = products.filter(price__lte=max_price)

    if filters["in_stock"]:
        products = products.filter(stock__gt=0)

    sort_map = {
        "name_asc": "name",
        "name_desc": "-name",
        "price_asc": "price",
        "price_desc": "-price",
        "newest": "-created_at",
    }
    sort_field = sort_map.get(raw_sort)
    if sort_field:
        products = products.order_by(sort_field)

    context = {
        "products": products,
        "categories": categories,
        "filters": filters,
    }
    return render(request, "store/product_list.html", context)


def product_detail(request, pk):
    product = get_object_or_404(
        # Evita accesos directos a productos "desactivados" desde URL.
        Product.objects.select_related("category").filter(is_active=True),
        pk=pk,
    )
    return render(request, "store/product_detail.html", {"product": product})


# =========================
# Carrito
# =========================

@login_required
@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)

    # Carrito = diccionario en sesiÃ³n (id_producto -> cantidad)
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

    # Evita que la suma en el carrito supere el stock actual del producto.
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
    """
    Redirige de forma segura a una URL entregada por el cliente.

    Se usa para volver al catalogo/detalle sin aceptar redirecciones abiertas
    (open redirect). Si `next`/referer no es valido, cae al `fallback_url`.
    """
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

    # Si un producto se desactiva, lo ocultamos del carrito para evitar compras
    # de productos no disponibles publicamente.
    products = (
        Product.objects.filter(id__in=product_ids, is_active=True)
        .select_related("category")
    )

    # Limpieza del carrito: elimina ids inexistentes/inactivos para evitar
    # inconsistencias entre la sesion y lo que se muestra en pantalla.
    active_ids = {str(product.id) for product in products}
    removed_ids = [product_id for product_id in list(cart.keys()) if product_id not in active_ids]
    if removed_ids:
        for product_id in removed_ids:
            cart.pop(product_id, None)
        request.session["cart"] = cart
        request.session.modified = True
        messages.info(
            request,
            "Se removieron del carrito algunos productos que ya no estan disponibles.",
        )

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
    product = get_object_or_404(Product, pk=pk, is_active=True)

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

    # Validacion de stock contra la cantidad solicitada.
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
@require_POST
def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)

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

    # Resolucion en bloque de productos activos (evita 404 si el carrito quedó viejo).
    normalized_ids = []
    for raw_id in cart.keys():
        try:
            normalized_ids.append(int(raw_id))
        except (TypeError, ValueError):
            continue

    products = Product.objects.filter(id__in=normalized_ids, is_active=True)
    product_map = {str(product.id): product for product in products}

    removed_ids = []
    for product_id, quantity in cart.items():
        product = product_map.get(str(product_id))
        if not product:
            removed_ids.append(str(product_id))
            continue

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            removed_ids.append(str(product_id))
            continue

        if quantity < 1:
            removed_ids.append(str(product_id))
            continue

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    if removed_ids:
        for product_id in removed_ids:
            cart.pop(str(product_id), None)
        request.session["cart"] = cart
        request.session.modified = True
        messages.info(
            request,
            "Se actualizó tu carrito porque algunos productos ya no están disponibles.",
        )
        if not cart_items:
            messages.warning(request, "Tu carrito está vacío.")
            return redirect("store:cart_detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.is_completed = False
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

            # Marcamos como completada solo cuando todos los items fueron creados
            # y el stock fue actualizado.
            order.is_completed = True
            order.save(update_fields=["is_completed"])

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
