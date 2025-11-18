# Sistema de Reserva de Salas de Biblioteca

Sistema de gestión y reserva de salas de estudio desarrollado con Django y PostgreSQL.

## Características

- Gestión de salas de estudio (CRUD completo)
- Sistema de reservas con validación de RUT chileno (módulo 11)
- Restricción: un RUT solo puede tener una reserva activa a la vez
- Duración automática de reservas: 2 horas
- Liberación automática de salas
- Panel de administración Django

## Tecnologías

- Python 3.x
- Django 5.x
- PostgreSQL
- django-environ

## Instalación

1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno virtual
4. Instalar dependencias: `pip install django psycopg2-binary django-environ`
5. Crear archivo `.env` con las credenciales de la base de datos
6. Ejecutar migraciones: `python manage.py migrate`
7. Crear superusuario: `python manage.py createsuperuser`
8. Ejecutar servidor: `python manage.py runserver`
