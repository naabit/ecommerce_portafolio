"""
Context processors de la app `store`.

Se utilizan para exponer datos del carrito a los templates,
incluyendo un contador global y una vista previa para el offcanvas.
"""

def cart_item_count(request):
    """Agrega `cart_item_count` y (opcionalmente) un preview del carrito al contexto."""
    cart = request.session.get("cart", {}) or {}

    try:
        total_items = sum(int(value) for value in cart.values())
    except (TypeError, ValueError):
        total_items = 0

    context = {"cart_item_count": total_items}

    # Solo armamos la vista previa del carrito si el usuario está autenticado,
    # porque el botón flotante/offcanvas se oculta para usuarios anónimos.
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return context

    # Vista previa para el offcanvas del carrito.
    # Importamos aquí para evitar costos/ciclos de import en requests anónimos.
    from decimal import Decimal
    from .models import Product

    product_ids = []
    for product_id in cart.keys():
        try:
            product_ids.append(int(product_id))
        except (TypeError, ValueError):
            continue

    products = Product.objects.filter(id__in=product_ids, is_active=True).only(
        "id",
        "name",
        "price",
    )
    product_map = {str(product.id): product for product in products}

    preview_items = []
    preview_total = Decimal("0")

    for product_id, quantity in cart.items():
        product = product_map.get(str(product_id))
        if not product:
            continue

        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            continue
        if qty <= 0:
            continue

        subtotal = product.price * qty
        preview_total += subtotal
        preview_items.append(
            {
                "product": product,
                "quantity": qty,
                "subtotal": subtotal,
            }
        )

    context.update(
        {
            "cart_preview_items": preview_items,
            "cart_preview_total": preview_total,
        }
    )

    return context
