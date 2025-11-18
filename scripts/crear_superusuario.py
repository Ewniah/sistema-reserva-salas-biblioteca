import os
import sys
import django

# Agregar el directorio raíz al path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

print("👤 Creando superusuario admin...")

# Verificar si ya existe
if User.objects.filter(username='admin').exists():
    print("⚠️  El usuario 'admin' ya existe.")
    respuesta = input("¿Desea eliminarlo y crear uno nuevo? (s/n): ")
    if respuesta.lower() == 's':
        User.objects.filter(username='admin').delete()
        print("✓ Usuario anterior eliminado")
    else:
        print("❌ Operación cancelada")
        exit()

# Crear nuevo superusuario
User.objects.create_superuser(
    username='admin',
    email='admin@biblioteca.cl',
    password='Admin1234'
)

print("\n✅ ¡Superusuario creado exitosamente!")
print("\n📋 Credenciales:")
print("   Usuario: admin")
print("   Contraseña: Admin1234")
print("   Email: admin@biblioteca.cl")
print("\n🔗 URLs de acceso:")
print("   Panel Admin Personalizado: http://127.0.0.1:8000/panel-admin/")
print("   Django Admin: http://127.0.0.1:8000/admin/")
print("\n🚀 ¡Listo para usar!")
