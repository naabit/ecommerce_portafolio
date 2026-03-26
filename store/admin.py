from django.contrib import admin
from .models import Category, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "stock")
    list_filter = ("category",)
    search_fields = ("name", "description")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "email", "city", "created_at", "is_completed")
    list_filter = ("is_completed", "created_at", "city")
    search_fields = ("full_name", "email", "user__username")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "price", "quantity", "subtotal")
    search_fields = ("product__name", "order__full_name")

    @admin.display(description="Subtotal")
    def subtotal(self, obj):
        return obj.subtotal