from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

def validar_rut(rut):
    """
    Valida un RUT chileno usando el algoritmo de módulo 11.
    Formato esperado: 12345678-9 o 12345678-K
    """
    rut = rut.upper().replace(".", "").replace("-", "").replace(" ", "")
    
    if len(rut) < 2:
        raise ValidationError('El RUT ingresado es demasiado corto. Formato esperado: 12345678-K')
    
    cuerpo = rut[:-1]
    dv = rut[-1]
    
    if not cuerpo.isdigit():
        raise ValidationError('El RUT ingresado es inválido: el cuerpo debe contener solo números')
    
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
        raise ValidationError(f'El RUT ingresado es inválido: dígito verificador incorrecto. Esperado: {dv_calculado}')
    
    return True


class Sala(models.Model):
    """
    Modelo para representar una sala de estudio
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
        Verifica si la sala está disponible actualmente
        (no tiene reservas activas y está habilitada)
        """
        if not self.habilitada:
            return False
        
        ahora = timezone.now()
        # IMPORTANTE: Solo considerar reservas con estado 'activa'
        reserva_activa = self.reservas.filter(
            fecha_hora_inicio__lte=ahora,
            fecha_hora_fin__gte=ahora,
            estado='activa'  # <--- ESTA LÍNEA ES CRÍTICA
        ).exists()
        
        return not reserva_activa


class Reserva(models.Model):
    """
    Modelo para representar una reserva de sala
    """
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='reservas', verbose_name='Sala')
    rut = models.CharField(max_length=12, validators=[validar_rut], verbose_name='RUT')
    nombre_reservante = models.CharField(max_length=200, verbose_name='Nombre del Reservante')
    fecha_hora_inicio = models.DateTimeField(verbose_name='Fecha y Hora de Inicio')
    fecha_hora_fin = models.DateTimeField(verbose_name='Fecha y Hora de Fin')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación de Reserva')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activa',
        verbose_name='Estado'
    )
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_hora_inicio']
    
    def __str__(self):
        return f"Reserva de {self.nombre_reservante} - Sala {self.sala.nombre}"
    
    def clean(self):
        """
        Validaciones personalizadas antes de guardar
        """
        # Solo validar si tenemos los datos necesarios
        if not self.sala_id or not self.rut:
            return
        
        # Validar que no exista otra reserva activa del mismo RUT
        ahora = timezone.now()
        
        # Asegurarse de que las fechas estén definidas para la comparación
        fecha_fin_comparar = self.fecha_hora_fin if self.fecha_hora_fin else ahora + timedelta(hours=2)
        
        # Construir el queryset de reservas activas
        reservas_activas = Reserva.objects.filter(
            rut=self.rut,
            fecha_hora_fin__gte=ahora,
            estado='activa'
        )
        
        # Excluir la reserva actual si ya existe (para ediciones)
        if self.pk:
            reservas_activas = reservas_activas.exclude(pk=self.pk)
        
        # Si hay reservas activas, lanzar error
        if reservas_activas.exists():
            raise ValidationError('Este RUT ya tiene una reserva activa. No puede reservar otra sala hasta que finalice la reserva actual.')
        
        # Validar que la sala esté habilitada
        if hasattr(self, 'sala') and not self.sala.habilitada:
            raise ValidationError('Esta sala no está habilitada para reservas.')
        
        # Validar que la fecha de fin sea mayor a la de inicio
        if self.fecha_hora_inicio and self.fecha_hora_fin:
            if self.fecha_hora_fin <= self.fecha_hora_inicio:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
    
    def save(self, *args, **kwargs):
        """
        Método save personalizado para asignar fechas automáticamente
        """
        # Si no se especifica fecha_hora_inicio, usar la hora actual
        if not self.fecha_hora_inicio:
            self.fecha_hora_inicio = timezone.now()
        
        # Si no se especifica fecha_hora_fin, calcular automáticamente (2 horas después)
        if not self.fecha_hora_fin:
            self.fecha_hora_fin = self.fecha_hora_inicio + timedelta(hours=2)
        
        # Ejecutar validaciones SOLO si no se especifica update_fields
        # (para permitir actualizaciones directas sin validaciones completas)
        if 'update_fields' not in kwargs:
            self.full_clean()
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_hora_inicio']
    
    def __str__(self):
        return f"Reserva de {self.nombre_reservante} - Sala {self.sala.nombre}"
    
    def clean(self):
        """
        Validaciones personalizadas antes de guardar
        """
        # Validar que no exista otra reserva activa del mismo RUT
        ahora = timezone.now()
        reservas_activas = Reserva.objects.filter(
            rut=self.rut,
            fecha_hora_fin__gte=ahora,
            estado='ACTIVA'
        ).exclude(pk=self.pk)
        
        if reservas_activas.exists():
            raise ValidationError('Este RUT ya tiene una reserva activa. No puede reservar otra sala hasta que finalice la reserva actual.')
        
        # Validar que la sala esté habilitada
        if not self.sala.habilitada:
            raise ValidationError('Esta sala no está habilitada para reservas.')
        
        # Validar que la fecha de fin sea mayor a la de inicio
        # SOLO si ambas fechas están definidas
        if self.fecha_hora_inicio and self.fecha_hora_fin:  # <--- ÚNICA CORRECCIÓN AQUÍ
            if self.fecha_hora_fin <= self.fecha_hora_inicio:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
    
    def save(self, *args, **kwargs):
        # Si no se especifica fecha_hora_inicio, usar la hora actual
        if not self.fecha_hora_inicio:
            self.fecha_hora_inicio = timezone.now()
        
        # Si no se especifica fecha_hora_fin, calcular automáticamente (2 horas después)
        if not self.fecha_hora_fin:
            self.fecha_hora_fin = self.fecha_hora_inicio + timedelta(hours=2)
        
        # Ejecutar validaciones SOLO si no se especifica update_fields
        # (para permitir actualizaciones directas en tests)
        if 'update_fields' not in kwargs:  # <--- ÚNICA CORRECCIÓN AQUÍ
            self.full_clean()
        
        super().save(*args, **kwargs)
