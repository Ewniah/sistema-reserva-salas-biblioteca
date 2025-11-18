from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

# Función para validar RUT chileno con módulo 11
def validar_rut(rut):
    """
    Se valida un RUT chileno utilizando el algoritmo de módulo 11.
    Formato esperado: XXXXXXXX-Y donde Y es el dígito verificador (0-9 o K)
    """
    rut = rut.upper().replace(".", "").replace("-", "")
    
    if len(rut) < 2:
        raise ValidationError('El RUT ingresado es demasiado corto. Formato esperado: 12345678-K')
    
    cuerpo = rut[:-1]
    dv = rut[-1]
    
    if not cuerpo.isdigit():
        raise ValidationError('El RUT ingresado contiene caracteres inválidos en el cuerpo numérico.')
    
    # Algoritmo de módulo 11
    suma = 0
    multiplicador = 2
    
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador == 8:
            multiplicador = 2
    
    resto = suma % 11
    dv_calculado = 11 - resto
    
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)
    
    if dv != dv_calculado:
        raise ValidationError(f'El RUT ingreasdo es inválido: dígito verificador incorrecto. Esperado: {dv_calculado}')
    
    return True


class Sala(models.Model):
    """
    Modelo para representar una sala de estudio o reunión
    """
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre de la Sala')
    capacidad = models.IntegerField(verbose_name='Capacidad')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    habilitada = models.BooleanField(default=True, verbose_name='Habilitada')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    
    class Meta:
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} (Capacidad: {self.capacidad})"
    
    def esta_disponible(self):
        """
        Verifica si la sala actual está disponible para reserva
        (No tiene reservas activas y está habilitada para reservas)
        """
        if not self.habilitada:
            return False
        
        ahora = timezone.now()
        reserva_activa = self.reservas.filter(
            fecha_hora_inicio__lte=ahora,
            fecha_hora_fin__gte=ahora
        ).exists()
        
        return not reserva_activa


class Reserva(models.Model):
    """
    Modelo para representar una reserva de sala
    """
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='reservas', verbose_name='Sala')
    rut = models.CharField(max_length=12, validators=[validar_rut], verbose_name='RUT')
    nombre_reservante = models.CharField(max_length=200, verbose_name='Nombre del Reservante')
    fecha_hora_inicio = models.DateTimeField(verbose_name='Fecha y Hora de Inicio')
    fecha_hora_fin = models.DateTimeField(verbose_name='Fecha y Hora de Fin')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación de Reserva')
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_hora_inicio']
    
    def __str__(self):
        return f"Reserva de {self.nombre_reservante} - Sala {self.sala.nombre}"
    
    def clean(self):
        """
        Validaciones personalizadas antes de guardar la reserva
        1. Un RUT no puede tener más de una reserva activa al mismo tiempo.
        """
        # Validar que el RUT no tenga reservas activas
        ahora = timezone.now()
        reservas_activas = Reserva.objects.filter(
            rut=self.rut,
            fecha_hora_fin__gte=ahora
        ).exclude(pk=self.pk)
        
        if reservas_activas.exists():
            raise ValidationError('El RUT ingresado ya tiene una reserva activa. No puede reservar otra sala hasta que finalice la reserva actual.')
        
        # Validar que la sala esté habilitada
        if not self.sala.habilitada:
            raise ValidationError('Esta sala no está habilitada para reservas.')
        
        # Validar que la fecha de fin sea mayor a la de inicio
        if self.fecha_hora_fin <= self.fecha_hora_inicio:
            raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
    
    def save(self, *args, **kwargs):
        # Si no se especifica fecha_hora_inicio, usar la hora actual
        if not self.fecha_hora_inicio:
            self.fecha_hora_inicio = timezone.now()
        
        # Si no se especifica fecha_hora_fin, calcular automáticamente (2 horas después)
        if not self.fecha_hora_fin:
            self.fecha_hora_fin = self.fecha_hora_inicio + timedelta(hours=2)
        
        # Ejecutar validaciones
        self.full_clean()
        
        super().save(*args, **kwargs)
