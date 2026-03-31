from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from store.models import Category, Product


class Command(BaseCommand):
    help = "Puebla la base de datos con datos iniciales (grupos, usuarios, categorías y productos)."

    def handle(self, *args, **kwargs):
        # Comando de apoyo para evaluaciÃ³n/demo:
        # - crea usuarios de prueba (cliente/staff/admin)
        # - crea categorÃ­as y productos para el catÃ¡logo
        self.stdout.write(self.style.WARNING("Iniciando seed de datos..."))

        self.create_groups()
        self.create_users()
        self.create_categories()
        self.create_products()

        self.stdout.write(self.style.SUCCESS("Seed completado correctamente."))

    # ------------------------
    # GRUPOS
    # ------------------------
    def create_groups(self):
        cliente_group, _ = Group.objects.get_or_create(name="cliente")
        staff_group, _ = Group.objects.get_or_create(name="staff")

        # ------------------------
        # PERMISOS PARA PRODUCT
        # ------------------------
        product_ct = ContentType.objects.get_for_model(Product)

        product_permissions = Permission.objects.filter(
            content_type=product_ct,
            codename__in=[
                "view_product",
                "add_product",
                "change_product",
            ],
        )

        staff_group.permissions.add(*product_permissions)

        # ------------------------
        # PERMISOS PARA ORDER 
        # ------------------------
        try:
            from store.models import Order

            order_ct = ContentType.objects.get_for_model(Order)

            order_permissions = Permission.objects.filter(
                content_type=order_ct,
                codename__in=[
                    "view_order",
                    "change_order",
                ],
            )

            staff_group.permissions.add(*order_permissions)

        except Exception:
            self.stdout.write("Modelo Order no encontrado, se omiten permisos de orden.")

        self.stdout.write(self.style.SUCCESS("Grupos y permisos configurados."))
    # ------------------------
    # USUARIOS
    # ------------------------
    def create_users(self):
        User = get_user_model()

        cliente_group = Group.objects.get(name="cliente")
        staff_group = Group.objects.get(name="staff")

        users_data = [
            {
                "username": "cliente_demo",
                "email": "cliente@example.com",
                "password": "Cliente1234",
                "group": cliente_group,
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "staff_demo",
                "email": "staff@example.com",
                "password": "Staff1234",
                "group": staff_group,
                "is_staff": True,
                "is_superuser": False,
            },
            {
                "username": "admin_demo",
                "email": "admin@example.com",
                "password": "Admin1234",
                "group": staff_group,
                "is_staff": True,
                "is_superuser": True,
            },
        ]

        for data in users_data:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                },
            )

            if created:
                user.set_password(data["password"])
                user.is_staff = data["is_staff"]
                user.is_superuser = data["is_superuser"]
                user.save()

                user.groups.add(data["group"])

                self.stdout.write(self.style.SUCCESS(f"Usuario creado: {user.username}"))
            else:
                self.stdout.write(f"Usuario ya existente: {user.username}")

    # ------------------------
    # CATEGORÍAS
    # ------------------------
    def create_categories(self):
        categories_data = [
            ("Audio", "Productos de sonido y música."),
            ("Periféricos", "Teclados, mouse y accesorios."),
            ("Accesorios", "Complementos tecnológicos."),
            ("Oficina", "Productos para estudio y trabajo."),
        ]

        for name, description in categories_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Categoría creada: {name}"))
            else:
                self.stdout.write(f"Categoría ya existente: {name}")

    # ------------------------
    # PRODUCTOS
    # ------------------------
    def create_products(self):
        categories = {c.name: c for c in Category.objects.all()}

        products_data = [
            ("Auriculares Bluetooth Indigo", "Audio", 39990, 12),
            ("Parlante Mini Pulse", "Audio", 24990, 8),
            ("Teclado Mecánico Nova", "Periféricos", 45990, 10),
            ("Mouse Inalámbrico Orbit", "Periféricos", 18990, 15),
            ("Base Notebook Elevate", "Accesorios", 21990, 9),
            ("Mochila Urbana Slate", "Accesorios", 34990, 7),
            ("Lámpara Escritorio Halo", "Oficina", 27990, 11),
            ("Organizador Grid", "Oficina", 14990, 20),
            ("Cuaderno Ejecutivo", "Oficina", 9990, 25),
            ("Cable USB-C Pro", "Accesorios", 7990, 30),
        ]

        for name, category_name, price, stock in products_data:
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "description": f"{name} de alta calidad para uso diario.",
                    "price": Decimal(price),
                    "stock": stock,
                    "category": categories[category_name],
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Producto creado: {name}"))
            else:
                self.stdout.write(f"Producto ya existente: {name}")
