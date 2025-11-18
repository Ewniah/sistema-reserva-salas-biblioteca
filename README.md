================================================================================
SISTEMA DE RESERVA DE SALAS DE BIBLIOTECA
================================================================================

Sistema completo de gestión y reserva de salas de estudio desarrollado con
Django y PostgreSQL.

================================================================================
CARACTERÍSTICAS
================================================================================

- Gestión de salas (CRUD completo) - Crear, editar, eliminar y listar salas
- Sistema de reservas - Los usuarios pueden reservar salas disponibles
- Validación de RUT chileno - Implementado con algoritmo módulo 11
- Restricción por RUT - Un RUT solo puede tener una reserva activa a la vez
- Duración automática - Las reservas tienen 2 horas de duración automática
- Liberación automática - Las salas se liberan automáticamente al finalizar
- Panel de administración personalizado - Gestión completa con estadísticas
- Sistema de autenticación - Login/logout para administradores
- Finalizar reservas anticipadamente - Los admin pueden finalizar reservas

================================================================================
TECNOLOGÍAS UTILIZADAS
================================================================================

- Python 3.14
- Django 5.2
- PostgreSQL
- django-environ - Manejo de variables de entorno
- psycopg2-binary - Adaptador de PostgreSQL

================================================================================
INSTALACIÓN
================================================================================

## REQUISITOS PREVIOS

- Python 3.10 o superior
- PostgreSQL instalado y corriendo
- Git

## PASOS DE INSTALACIÓN

1. Clonar el repositorio:
   git clone https://github.com/tu-usuario/sistema-reserva-salas-biblioteca.git
   cd sistema-reserva-salas-biblioteca

2. Crear y activar entorno virtual:

   Windows:
   python -m venv venv
   venv\Scripts\activate

   Mac/Linux:
   python3 -m venv venv
   source venv/bin/activate

3. Instalar dependencias:
   pip install -r requirements.txt

4. Configurar la base de datos PostgreSQL:

   Ejecutar en PostgreSQL:
   CREATE DATABASE biblioteca_db;
   CREATE USER biblioteca_user WITH PASSWORD 'tu_password';
   ALTER ROLE biblioteca_user SET client_encoding TO 'utf8';
   ALTER ROLE biblioteca_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE biblioteca_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE biblioteca_db TO biblioteca_user;

5. Configurar variables de entorno:

   Crear archivo .env en la raíz del proyecto:
   DB_NAME=biblioteca_db
   DB_USER=biblioteca_user
   DB_PASSWORD=tu_password
   DB_HOST=127.0.0.1
   DB_PORT=5432
   SECRET_KEY=tu_clave_secreta_aqui

   Generar SECRET_KEY:
   python generar_secret_key.py

6. Ejecutar migraciones:
   python manage.py migrate

7. Crear superusuario:
   python manage.py createsuperuser

8. Cargar datos de prueba (opcional):
   python cargar_datos.py

9. Ejecutar el servidor:
   python manage.py runserver

10. Acceder al sistema:
    - Página principal: http://127.0.0.1:8000/
    - Panel admin personalizado: http://127.0.0.1:8000/panel-admin/
    - Admin Django: http://127.0.0.1:8000/admin/

================================================================================
EJECUTAR TESTS
================================================================================

python manage.py test

Resultado esperado:
Ran 26 tests in X.XXXs
OK

================================================================================
ESTRUCTURA DEL PROYECTO
================================================================================

sistema-reserva-salas-biblioteca/
├── config/ # Configuración del proyecto
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
├── salas/ # Aplicación principal
│ ├── migrations/
│ ├── templates/ # Plantillas HTML
│ │ ├── admin/ # Templates del panel admin
│ │ └── salas/ # Templates públicos
│ ├── admin.py
│ ├── forms.py
│ ├── models.py
│ ├── tests.py
│ ├── urls.py
│ └── views.py
├── .env # Variables de entorno (NO en GitHub)
├── .gitignore
├── cargar_datos.py # Script para cargar datos de prueba
├── generar_secret_key.py # Script para generar SECRET_KEY
├── manage.py
├── README.md
└── requirements.txt

================================================================================
CREDENCIALES DE PRUEBA
================================================================================

Después de ejecutar "python cargar_datos.py":

SALAS CREADAS:

- Sala A - Silenciosa (Capacidad: 4)
- Sala B - Grupal (Capacidad: 8)
- Sala C - Multimedia (Capacidad: 6)
- Sala D - Conferencias (Capacidad: 12)
- Sala E - Estudio (Capacidad: 2)

RESERVAS DE EJEMPLO:

- RUT: 11111111-1
- RUT: 22222222-2

================================================================================
FUNCIONALIDADES PRINCIPALES
================================================================================

PARA USUARIOS:

- Ver salas disponibles
- Reservar salas (2 horas automáticas)
- Consultar mis reservas por RUT
- Validación de RUT chileno con módulo 11

PARA ADMINISTRADORES:

- Panel de estadísticas en tiempo real
- CRUD completo de salas
- Gestión de reservas
- Finalizar reservas anticipadamente
- Habilitar/deshabilitar salas

================================================================================
VALIDACIONES IMPLEMENTADAS
================================================================================

✓ RUT chileno validado con módulo 11
✓ Un RUT solo puede tener una reserva activa
✓ Solo se pueden reservar salas habilitadas
✓ Duración automática de 2 horas
✓ Liberación automática de salas
✓ Verificación de disponibilidad en tiempo real

================================================================================
