# Purple Store

E-commerce desarrollado con Django, PostgreSQL y Bootstrap 5. El proyecto implementa un flujo de compra funcional que incluye catálogo, carrito, autenticación, checkout y generación de órdenes.

Está pensado como proyecto de portafolio para demostrar desarrollo backend con Django, persistencia de datos, manejo de sesiones, autenticación de usuarios y despliegue en producción.

## Demo

Aplicación desplegada en Render:

https://ecommerce-portafolio.onrender.com

## Características principales

* Catálogo de productos almacenado en base de datos.
* Visualización de productos por categoría.
* Detalle individual de cada producto.
* Carrito de compras basado en sesión.
* Registro, inicio y cierre de sesión de usuarios.
* Checkout con creación de órdenes y detalle de productos comprados.
* Asociación de órdenes a usuarios autenticados.
* Mensajes de confirmación y error durante la navegación.
* Panel de administración mediante Django Admin.
* Gestión de stock desde el modelo de productos.
* Interfaz responsive construida con Bootstrap 5.
* Comando de carga inicial para categorías, productos y usuarios de demostración.

## Tecnologías

* Python
* Django
* PostgreSQL
* Bootstrap 5
* HTML
* CSS
* Gunicorn
* WhiteNoise
* Render

## Estructura general

```text
ecommerce_portafolio/
├── config/                 # Configuración principal de Django
├── core/                   # Vistas y páginas generales
├── store/                  # Catálogo, carrito, checkout y órdenes
│   └── management/
│       └── commands/
│           └── seed_data.py
├── users/                  # Registro, login y manejo de usuarios
├── static/                 # Archivos estáticos del proyecto
├── templates/              # Templates globales
├── build.sh                # Script de construcción para despliegue
├── manage.py
├── requirements.txt
└── runtime.txt
```

## Instalación local

Clona el repositorio:

```bash
git clone https://github.com/naabit/ecommerce_portafolio.git
cd ecommerce_portafolio
```

Crea y activa un entorno virtual:

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### macOS o Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Configuración de variables de entorno

Crea un archivo llamado `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu_clave_secreta_de_django
DEBUG=True
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/ecommerce_db
```

Para producción, `DEBUG` debe estar configurado como:

```env
DEBUG=False
```

En Render, las variables de entorno se configuran desde el panel del servicio web. La aplicación requiere, como mínimo:

```env
SECRET_KEY=tu_clave_secreta
DEBUG=False
DATABASE_URL=postgresql://usuario:password@host:puerto/nombre_base_de_datos
```

## Base de datos local

Crea una base de datos PostgreSQL:

```sql
CREATE DATABASE ecommerce_db;
```

Luego aplica las migraciones:

```bash
python manage.py migrate
```

## Datos iniciales

El proyecto incluye un comando para crear categorías, productos, grupos y usuarios de demostración.

```bash
python manage.py seed_data
```

El comando puede ejecutarse más de una vez sin duplicar categorías ni productos, ya que utiliza `get_or_create`.

Para fines de desarrollo local, crea los siguientes usuarios:

```text
cliente_demo
staff_demo
admin_demo
```

Por seguridad, las credenciales de administración no deben usarse en una instancia pública de producción. En un entorno desplegado, se recomienda crear un superusuario propio con una contraseña privada:

```bash
python manage.py createsuperuser
```

## Ejecutar el proyecto

```bash
python manage.py runserver
```

Luego abre:

```text
http://127.0.0.1:8000/
```

## Rutas principales

### Públicas

```text
/
 /about/
 /store/
 /store/producto/<id>/
```

### Compra

```text
/store/carrito/
/store/checkout/
/store/checkout/exito/<id>/
```

### Usuarios

```text
/users/login/
/users/register/
/users/logout/
```

### Administración

```text
/admin/
```

## Despliegue

La aplicación está preparada para desplegarse en Render.

El archivo `build.sh` ejecuta la instalación de dependencias, la recolección de archivos estáticos, las migraciones y la carga de datos iniciales:

```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_data
```

Para que el despliegue funcione correctamente, el servicio web debe tener configurada la variable `DATABASE_URL` con la URL interna de la base de datos PostgreSQL creada en Render.

## Próximas mejoras

* Integración con una pasarela de pagos.
* Historial de compras para usuarios autenticados.
* Filtros y búsqueda avanzada de productos.
* Paginación del catálogo.
* Gestión de imágenes de productos desde Django Admin.
* Pruebas automatizadas para carrito, checkout y autenticación.
* Confirmación de compra por correo electrónico.
* Mejoras de accesibilidad y experiencia móvil.

## Autoría

Desarrollado por Natalia García Cofré como proyecto de portafolio enfocado en desarrollo backend con Django, bases de datos relacionales y construcción de flujos funcionales de e-commerce.
