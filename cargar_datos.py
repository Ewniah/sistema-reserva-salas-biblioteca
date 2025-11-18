"""
Script para cargar datos de ejemplo en la base de datos del sistema de reserva de salas de estudio.
Permite crear salas de estudio y reservas de ejemplo para facilitar las pruebas y demostraciones.
Ejecutar con: python cargar_datos.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from salas.models import Sala, Reserva
from django.utils import timezone
from datetime import timedelta

def cargar_salas():
    """
    Crea salas de estudio de ejemplo
    """
    print("Cargando salas de estudio...")
    
    salas_data = [
        {
            'nombre': 'Sala A - Silenciosa',
            'capacidad': 4,
            'descripcion': 'Sala tranquila ideal para estudio individual o en grupos pequeños.',
            'habilitada': True,
        },
        {
            'nombre': 'Sala B - Grupal',
            'capacidad': 8,
            'descripcion': 'Sala amplia equipada con pizarra para trabajo en equipo.',
            'habilitada': True,
        },
        {
            'nombre': 'Sala C - Multimedia',
            'capacidad': 6,
            'descripcion': 'Sala con proyector y computador para presentaciones.',
            'habilitada': True,
        },
        {
            'nombre': 'Sala D - Conferencias',
            'capacidad': 12,
            'descripcion': 'Sala grande ideal para reuniones y seminarios.',
            'habilitada': True,
        },
        {
            'nombre': 'Sala E - Estudio',
            'capacidad': 2,
            'descripcion': 'Sala pequeña para estudio individual o parejas.',
            'habilitada': True,
        },
    ]
    
    salas_creadas = 0
    for sala_info in salas_data:
        sala, created = Sala.objects.get_or_create(
            nombre=sala_info['nombre'],
            defaults=sala_info
        )
        if created:
            salas_creadas += 1
            print(f"✓ Creada: {sala.nombre}")
        else:
            print(f"○ Ya existe: {sala.nombre}")
    
    print(f"\nTotal de salas creadas: {salas_creadas}")
    print(f"Total de salas en BD: {Sala.objects.count()}\n")


def cargar_reservas():
    """
    Crea algunas reservas de ejemplo
    """
    print("Cargando reservas de ejemplo...")
    
    # Verificar que existan salas
    if not Sala.objects.exists():
        print("❌ No hay salas disponibles. Ejecuta primero cargar_salas()")
        return
    
    # Obtener algunas salas
    salas = Sala.objects.filter(habilitada=True)[:3]
    
    reservas_data = [
        {
            'sala': salas[0] if len(salas) > 0 else None,
            'rut': '11111111-1',
            'nombre_reservante': 'Juan Pérez González',
        },
        {
            'sala': salas[1] if len(salas) > 1 else None,
            'rut': '22222222-2',
            'nombre_reservante': 'María López Silva',
        },
    ]
    
    reservas_creadas = 0
    ahora = timezone.now()
    
    for reserva_info in reservas_data:
        if reserva_info['sala'] is None:
            continue
            
        # Verificar si el RUT ya tiene una reserva activa
        tiene_reserva = Reserva.objects.filter(
            rut=reserva_info['rut'],
            fecha_hora_fin__gte=ahora
        ).exists()
        
        if not tiene_reserva:
            reserva = Reserva.objects.create(
                sala=reserva_info['sala'],
                rut=reserva_info['rut'],
                nombre_reservante=reserva_info['nombre_reservante'],
                fecha_hora_inicio=ahora,
                fecha_hora_fin=ahora + timedelta(hours=2)
            )
            reservas_creadas += 1
            print(f"✓ Reserva creada: {reserva.nombre_reservante} - {reserva.sala.nombre}")
        else:
            print(f"○ {reserva_info['nombre_reservante']} ya tiene una reserva activa")
    
    print(f"\nTotal de reservas creadas: {reservas_creadas}")
    print(f"Total de reservas activas: {Reserva.objects.filter(fecha_hora_fin__gte=ahora).count()}\n")


def limpiar_datos():
    """
    Elimina TODOS los datos de salas y reservas
    ¡CUIDADO! Esta acción no se puede deshacer
    """
    respuesta = input("⚠️  ¿Estás seguro de eliminar TODOS los datos? (si/no): ")
    if respuesta.lower() in ['si', 'sí', 's', 'yes', 'y']:
        Reserva.objects.all().delete()
        Sala.objects.all().delete()
        print("✓ Todos los datos han sido eliminados.\n")
    else:
        print("✗ Operación cancelada.\n")


def mostrar_estadisticas():
    """
    Muestra estadísticas de la base de datos
    """
    print("=" * 50)
    print("ESTADÍSTICAS DE LA BASE DE DATOS")
    print("=" * 50)
    
    total_salas = Sala.objects.count()
    salas_habilitadas = Sala.objects.filter(habilitada=True).count()
    
    print(f"\n📊 SALAS:")
    print(f"   Total de salas: {total_salas}")
    print(f"   Salas habilitadas: {salas_habilitadas}")
    print(f"   Salas deshabilitadas: {total_salas - salas_habilitadas}")
    
    ahora = timezone.now()
    total_reservas = Reserva.objects.count()
    reservas_activas = Reserva.objects.filter(fecha_hora_fin__gte=ahora).count()
    
    print(f"\n📅 RESERVAS:")
    print(f"   Total de reservas: {total_reservas}")
    print(f"   Reservas activas: {reservas_activas}")
    print(f"   Reservas finalizadas: {total_reservas - reservas_activas}")
    
    print("\n" + "=" * 50 + "\n")


def menu():
    """
    Menú interactivo para ejecutar las funciones
    """
    while True:
        print("\n" + "=" * 50)
        print("CARGADOR DE DATOS - Sistema de Reserva de Salas")
        print("=" * 50)
        print("\nOpciones:")
        print("1. Cargar salas de ejemplo")
        print("2. Cargar reservas de ejemplo")
        print("3. Cargar todo (salas + reservas)")
        print("4. Ver estadísticas")
        print("5. Limpiar todos los datos (¡CUIDADO!)")
        print("0. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            cargar_salas()
        elif opcion == '2':
            cargar_reservas()
        elif opcion == '3':
            cargar_salas()
            cargar_reservas()
        elif opcion == '4':
            mostrar_estadisticas()
        elif opcion == '5':
            limpiar_datos()
        elif opcion == '0':
            print("\n¡Hasta luego!\n")
            break
        else:
            print("\n❌ Opción inválida. Intente nuevamente.")


if __name__ == '__main__':
    print("\n🚀 Iniciando cargador de datos...\n")
    menu()
