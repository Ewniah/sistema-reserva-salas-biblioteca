import os
import sys
from django.core.management.utils import get_random_secret_key

# Agregar el directorio raíz al path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

print("🔐 Generando nueva SECRET_KEY para Django...\n")

secret_key = get_random_secret_key()

print("=" * 70)
print("SECRET_KEY generada:")
print("=" * 70)
print(f"\n{secret_key}\n")
print("=" * 70)

print("\n📋 Instrucciones:")
print("1. Copia la SECRET_KEY mostrada arriba")
print("2. Abre el archivo .env en la raíz del proyecto")
print("3. Busca la línea SECRET_KEY=...")
print("4. Reemplaza el valor con la nueva clave generada")
print("\nEjemplo en .env:")
print(f"SECRET_KEY={secret_key}")
print("\n✅ ¡Listo! Reinicia el servidor después de actualizar el .env")
