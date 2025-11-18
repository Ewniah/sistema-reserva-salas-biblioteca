from django.core.management.utils import get_random_secret_key # Se importa la función de Django para generar una clave secreta aleatoria

# Gennera y muestra una SECRET_KEY aleatoria con 50 caracteres para Django
print(get_random_secret_key())