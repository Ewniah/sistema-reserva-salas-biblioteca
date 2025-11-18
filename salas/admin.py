from django.contrib import admin
from .models import Sala, Reserva

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'habilitada', 'fecha_creacion')
    list_filter = ('habilitada',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('habilitada',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('sala', 'nombre_reservante', 'rut', 'fecha_hora_inicio', 'fecha_hora_fin')
    list_filter = ('sala', 'fecha_hora_inicio')
    search_fields = ('rut', 'nombre_reservante')
    date_hierarchy = 'fecha_hora_inicio'
