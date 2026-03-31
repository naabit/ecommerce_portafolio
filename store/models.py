"""
Modelos principales del e-commerce.

- `Category` y `Product` alimentan el catÃ¡logo.
- `Order` y `OrderItem` persisten compras confirmadas.
"""

from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings


def _sentence_case(value: str) -> str:
    # Helper reutilizable para normalizar strings ingresadas por el usuario.
    value = (value or "").strip()
    if not value:
        return value
    lowered = value.lower()
    return lowered[0].upper() + lowered[1:]

class Category(models.Model):
    """Agrupa productos para navegacion en el catalogo."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Producto vendible mostrado en el catalogo."""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Categoría",
    )
    name = models.CharField(max_length=150, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(1)],
        verbose_name="Precio",
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    image = models.URLField(blank=True, verbose_name="Imagen")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - ${self.price}"
    
class Order(models.Model):
    """Orden de compra confirmada (checkout completado)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        # Se permite null/blank por simplicidad (por ejemplo, si en el futuro
        # se habilita checkout como invitado). En el flujo actual se asigna
        # siempre el usuario autenticado.
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    # Se marca True solo cuando el checkout termina correctamente.
    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ["-created_at"]

    def __str__(self):
        username = getattr(self.user, "username", None) or "anonimo"
        return f"Orden #{self.id} - {username}"

    @property
    def total(self):
        """Total calculado como suma de subtotales de sus i­tems."""
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    """Detalle de un producto comprado dentro de una orden."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="order_items",
    )
    price = models.DecimalField(max_digits=10, decimal_places=0)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Ítem de orden"
        verbose_name_plural = "Ítems de orden"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity
