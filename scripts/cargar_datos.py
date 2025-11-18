import os
import sys
import django

# Agregar el directorio raíz al path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from salas.models import Sala, Reserva
from django.utils import timezone
from datetime import timedelta

print("📦 Cargando datos de ejemplo...")

# Crear salas modernas
salas_data = [
    {
        'nombre': 'Sala A - Silenciosa',
        'capacidad': 4,
        'descripcion': 'Sala ideal para estudio individual o en grupos pequeños. Ambiente silencioso.',
        'habilitada': True
    },
    {
        'nombre': 'Sala B - Grupal',
        'capacidad': 8,
        'descripcion': 'Espacio amplio para trabajo en equipo. Equipada con pizarra y proyector.',
        'habilitada': True
    },
    {
        'nombre': 'Sala C - Multimedia',
        'capacidad': 6,
        'descripcion': 'Sala con computadores y equipo de audio/video para presentaciones.',
        'habilitada': True
    },
    {
        'nombre': 'Sala D - Conferencias',
        'capacidad': 12,
        'descripcion': 'Sala grande para seminarios y conferencias. Aire acondicionado.',
        'habilitada': True
    },
    {
        'nombre': 'Sala E - Estudio Individual',
        'capacidad': 2,
        'descripcion': 'Pequeña sala para estudio personal o tutorías uno a uno.',
        'habilitada': True
    },
]

print("\n📚 Creando salas...")
for sala_info in salas_data:
    sala = Sala.objects.create(**sala_info)
    print(f"✓ Creada: {sala.nombre} (Capacidad: {sala.capacidad})")

# Crear algunas reservas de ejemplo con RUTs verídicos
print("\n📅 Creando reservas de ejemplo...")

ahora = timezone.now()

reservas_data = [
    {
        'sala': Sala.objects.get(nombre='Sala A - Silenciosa'),
        'rut': '13.180.096-7',
        'nombre_reservante': 'María González',
        'fecha_hora_inicio': ahora + timedelta(hours=1),
        'fecha_hora_fin': ahora + timedelta(hours=3),
        'estado': 'activa'
    },
    {
        'sala': Sala.objects.get(nombre='Sala B - Grupal'),
        'rut': '20.398.709-9',
        'nombre_reservante': 'Juan Pérez',
        'fecha_hora_inicio': ahora + timedelta(hours=2),
        'fecha_hora_fin': ahora + timedelta(hours=4),
        'estado': 'activa'
    },
    {
        'sala': Sala.objects.get(nombre='Sala C - Multimedia'),
        'rut': '13.205.573-4',
        'nombre_reservante': 'Ana Silva',
        'fecha_hora_inicio': ahora + timedelta(days=1),
        'fecha_hora_fin': ahora + timedelta(days=1, hours=2),
        'estado': 'activa'
    },
    {
        'sala': Sala.objects.get(nombre='Sala D - Conferencias'),
        'rut': '9.015.074-K',
        'nombre_reservante': 'Carlos Ramírez',
        'fecha_hora_inicio': ahora + timedelta(hours=3),
        'fecha_hora_fin': ahora + timedelta(hours=5),
        'estado': 'activa'
    },
]

for reserva_info in reservas_data:
    reserva = Reserva.objects.create(**reserva_info)
    print(f"✓ Reserva creada: {reserva.nombre_reservante} - {reserva.sala.nombre}")

print("\n✅ ¡Datos cargados exitosamente!")
print("\n📋 Resumen:")
print(f"   • {Sala.objects.count()} salas creadas")
print(f"   • {Reserva.objects.count()} reservas activas")

print("\n🔑 RUTs válidos para probar:")
print("   • 13.180.096-7 (María González) - Sala A")
print("   • 20.398.709-9 (Juan Pérez) - Sala B")
print("   • 13.205.573-4 (Ana Silva) - Sala C")
print("   • 9.015.074-K (Carlos Ramírez) - Sala D ✨ RUT con K")

print("\n👤 Credenciales de Admin:")
print("   Usuario: admin")
print("   Contraseña: Admin1234")
print("   URL: http://127.0.0.1:8000/panel-admin/")

print("\n🚀 Servidor listo para usar!")
