# Purple Store

**Purple Store** es una aplicación e-commerce desarrollada con Django, PostgreSQL y Bootstrap 5.

Implementa un flujo de compra funcional que incluye catálogo, categorías, carrito basado en sesión, autenticación de usuarios, checkout y generación de órdenes.

El proyecto fue desarrollado como parte de un portafolio para demostrar habilidades de desarrollo backend con Django, modelado de datos, persistencia con PostgreSQL, manejo de sesiones, autenticación, despliegue y documentación de calidad.

---

## Demo

Aplicación desplegada en Render:

https://ecommerce-portafolio.onrender.com

> La primera carga puede tardar algunos segundos si la instancia gratuita de Render estaba inactiva.

---

## Características principales

* Catálogo de productos almacenado en base de datos.
* Visualización de productos por categoría.
* Página de detalle individual para cada producto.
* Carrito de compras basado en sesión.
* Registro, inicio y cierre de sesión de usuarios.
* Checkout con creación de órdenes y detalle de productos comprados.
* Asociación de órdenes a usuarios autenticados.
* Mensajes de confirmación y error durante la navegación.
* Gestión de stock desde el modelo de productos.
* Panel de administración mediante Django Admin.
* Interfaz responsive construida con Bootstrap 5.
* Comando de carga inicial para categorías, productos y usuarios de demostración.

---

## Flujos principales

La aplicación permite recorrer un flujo de compra básico:

1. Explorar el catálogo y navegar por categorías.
2. Revisar el detalle de un producto.
3. Agregar, actualizar o eliminar productos del carrito.
4. Registrarse o iniciar sesión.
5. Acceder al checkout.
6. Crear una orden asociada al usuario autenticado.
7. Visualizar una confirmación de compra.

---

## Calidad y testing

El proyecto cuenta con un repositorio de QA separado que documenta pruebas manuales, pruebas exploratorias, evidencia visual, hallazgos y una automatización E2E inicial con Cypress.

[Visitar repositorio](https://github.com/naabit/ecommerce-testing-portfolio)

La cobertura actual considera principalmente los módulos de:

* Login.
* Carrito de compras.
* Checkout.

El repositorio de testing incluye:

* Plan de pruebas.
* Casos de prueba manuales.
* Registro de ejecución.
* Reportes de bugs.
* Evidencia visual.
* Prueba automatizada E2E del flujo de login con Cypress.

> La automatización E2E requiere levantar la aplicación localmente antes de ejecutarse. La documentación y los scripts de Cypress se mantienen en el repositorio QA para separar claramente el producto de la evidencia de testing.

---

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
* Cypress, para automatización E2E en el repositorio de QA

---

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

---

## Instalación local

Clona el repositorio:

```bash
git clone https://github.com/naabit/ecommerce_portafolio.git
cd ecommerce_portafolio
```

Crea y activa un entorno virtual.

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
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Configuración de variables de entorno

Crea un archivo llamado `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu_clave_secreta_de_django
DEBUG=True
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/ecommerce_db
```

Para producción:

```env
DEBUG=False
```

En Render, las variables se configuran desde el panel del servicio web. La aplicación requiere, como mínimo:

```env
SECRET_KEY=tu_clave_secreta
DEBUG=False
DATABASE_URL=postgresql://usuario:password@host:puerto/nombre_base_de_datos
```

> No subas el archivo `.env` al repositorio. Debe estar incluido en `.gitignore`.

---

## Base de datos local

Crea una base de datos PostgreSQL:

```sql
CREATE DATABASE ecommerce_db;
```

Luego aplica las migraciones:

```bash
python manage.py migrate
```

---

## Datos iniciales

El proyecto incluye un comando para crear categorías, productos, grupos y usuarios de demostración:

```bash
python manage.py seed_data
```

El comando puede ejecutarse más de una vez sin duplicar categorías ni productos, porque utiliza `get_or_create`.

Para desarrollo local, crea los siguientes usuarios de demostración:

```text
cliente_demo
staff_demo
admin_demo
```

Por seguridad, no utilices credenciales de administración conocidas en una instancia pública de producción. En un entorno desplegado, crea un superusuario propio con una contraseña privada:

```bash
python manage.py createsuperuser
```

---

## Ejecutar el proyecto

Con el entorno virtual activado:

```bash
python manage.py runserver
```

Luego abre:

```text
http://127.0.0.1:8000/
```

---

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

---

## Despliegue

La aplicación está preparada para desplegarse en Render.

El archivo `build.sh` instala dependencias, recopila archivos estáticos, aplica migraciones y ejecuta la carga inicial de datos:

```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_data
```

Para que el despliegue funcione correctamente, el servicio web debe tener configurada la variable `DATABASE_URL` con la URL interna de la base de datos PostgreSQL creada en Render.

---

## Limitaciones actuales

* La integración con pagos reales no está implementada.
* El proyecto usa una instancia de demostración y no debe utilizarse para transacciones reales.
* La carga inicial de productos depende del comando `seed_data`.
* La suite de automatización E2E se mantiene en un repositorio QA separado y actualmente cubre de forma inicial el flujo de login.
* Algunas mejoras de accesibilidad, validación y experiencia móvil siguen pendientes.

---

## Próximas mejoras

* Integrar una pasarela de pagos.
* Agregar historial de compras para usuarios autenticados.
* Incorporar filtros y búsqueda avanzada de productos.
* Agregar paginación del catálogo.
* Mejorar la gestión de imágenes de productos desde Django Admin.
* Extender la automatización E2E a carrito, checkout, registro y flujos negativos.
* Agregar pruebas unitarias e integración dentro del proyecto Django.
* Ejecutar pruebas automatizadas mediante GitHub Actions.
* Incorporar confirmación de compra por correo electrónico.
* Mejorar accesibilidad y experiencia en dispositivos móviles.

---

## Autoría

Desarrollado por **Natalia García Cofré** como proyecto de portafolio enfocado en desarrollo backend con Django, bases de datos relacionales, flujos funcionales de e-commerce y testing QA.
