# 🟣 Purple Store - E-commerce

Proyecto final de e-commerce desarrollado con **Django + PostgreSQL +
Bootstrap 5**, que implementa un flujo completo de compra:

-  **catálogo → carrito → checkout → confirmación**

------------------------------------------------------------------------

## 🔗 Repositorio

 -  *\[https://github.com/naabit/ecommerce_portafolio\]* 

------------------------------------------------------------------------

##  Características principales

-   🔐 Autenticación de usuarios (cliente, staff, admin)
-   🛍️ Catálogo de productos persistido en base de datos
-   🛒 Carrito de compras en sesión
-   📦 Checkout con generación de órdenes
-   🧾 Asociación de órdenes a usuarios autenticados
-   ⚙️ Panel de administración (Django Admin)
-   💬 Mensajes de feedback (éxito/error)
-   🎨 Interfaz responsive con Bootstrap 5

------------------------------------------------------------------------

## 🧱 Tecnologías utilizadas

-   Python 3.11+
-   Django
-   PostgreSQL
-   Bootstrap 5
-   HTML + CSS

------------------------------------------------------------------------

## ⚙️ Instalación (local)

``` bash
git clone https://github.com/naabit/ecommerce_portafolio
cd ecommerce_portafolio
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

------------------------------------------------------------------------

## 🔐 Configuración (.env)

Crear archivo `.env`:

    SECRET_KEY=tu_clave_secreta
    DEBUG=True
    DB_NAME=ecommerce_db
    DB_USER=postgres
    DB_PASSWORD=tu_password
    DB_HOST=localhost
    DB_PORT=5432

------------------------------------------------------------------------

## 🗄️ Base de datos

``` sql
CREATE DATABASE ecommerce_db;
```

``` bash
python manage.py migrate
```

------------------------------------------------------------------------

## 🌱 Datos de prueba

``` bash
python manage.py seed_data
```

### 🔑 Credenciales

-   cliente_demo / Cliente1234
-   staff_demo / Staff1234
-   admin_demo / Admin1234

------------------------------------------------------------------------

## ▶️ Ejecutar

``` bash
python manage.py runserver
```

-  http://127.0.0.1:8000/

------------------------------------------------------------------------

## 🌐 Rutas principales

### Públicas

-   /
-   /about/
-   /store/
-   /store/producto/`<id>`{=html}/

### Cliente

-   /store/carrito/
-   /store/checkout/
-   /store/checkout/exito/`<id>`{=html}/

### Auth

-   /users/login/
-   /users/register/
-   /users/logout/

### Admin

-   /admin/

------------------------------------------------------------------------



## 💡 Próximas mejoras

-   Pagos online
-   Historial de órdenes
-   Filtros avanzados
-   Deploy
