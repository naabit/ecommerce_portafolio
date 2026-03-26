from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
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