import os
import sys
import django

# Agregar el directorio raíz al path (directorio padre del script)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from salas.models import Sala, Reserva
from django.contrib.auth.models import User

print("🗑️  Limpiando base de datos...")

# Eliminar todas las reservas
reservas_count = Reserva.objects.count()
Reserva.objects.all().delete()
print(f"✓ Eliminadas {reservas_count} reservas")

# Eliminar todas las salas
salas_count = Sala.objects.count()
Sala.objects.all().delete()
print(f"✓ Eliminadas {salas_count} salas")

# Eliminar usuarios normales (mantener solo superusuarios)
usuarios_count = User.objects.filter(is_superuser=False).count()
User.objects.filter(is_superuser=False).delete()
print(f"✓ Eliminados {usuarios_count} usuarios normales")

print("\n✅ Base de datos limpiada correctamente!")
print("Ahora puedes cargar datos nuevos con: python scripts/cargar_datos.py")
