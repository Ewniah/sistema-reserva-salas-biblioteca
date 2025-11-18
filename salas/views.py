from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Sala, Reserva
from .forms import ReservaForm

def lista_salas(request):
    """
    Vista principal que muestra todas las salas disponibles
    """
    salas = Sala.objects.filter(habilitada=True)
    
    # Agregar información de disponibilidad a cada sala
    for sala in salas:
        sala.disponible = sala.esta_disponible()
    
    context = {
        'salas': salas,
        'titulo': 'Salas de Estudio Disponibles',
    }
    return render(request, 'salas/lista_salas.html', context)

def detalle_sala(request, sala_id):
    """
    Vista para mostrar el detalle de una sala específica
    """
    sala = get_object_or_404(Sala, id=sala_id)
    
    # Obtener reservas activas y futuras de esta sala
    ahora = timezone.now()
    reservas = sala.reservas.filter(fecha_hora_fin__gte=ahora).order_by('fecha_hora_inicio')
    
    context = {
        'sala': sala,
        'reservas': reservas,
        'disponible': sala.esta_disponible(),
    }
    return render(request, 'salas/detalle_sala.html', context)

def crear_reserva(request, sala_id):
    """
    Vista para crear una nueva reserva de sala
    """
    sala = get_object_or_404(Sala, id=sala_id)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            try:
                reserva = form.save(commit=False)
                # Las fechas se asignan automáticamente en el modelo
                reserva.save()
                messages.success(request, f'¡Reserva creada exitosamente! La sala {sala.nombre} está reservada por 2 horas.')
                return redirect('lista_salas')
            except Exception as e:
                messages.error(request, f'Error al crear la reserva: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        # Preseleccionar la sala actual
        form = ReservaForm(initial={'sala': sala})
    
    context = {
        'form': form,
        'sala': sala,
    }
    return render(request, 'salas/crear_reserva.html', context)

def mis_reservas(request):
    """
    Vista para que el usuario consulte sus reservas activas mediante su RUT
    """
    reservas = None
    rut_buscado = None
    
    if request.method == 'POST':
        rut_buscado = request.POST.get('rut', '').strip()
        if rut_buscado:
            # Limpiar el RUT
            rut_limpio = rut_buscado.replace('.', '').replace(' ', '').upper()
            if '-' not in rut_limpio and len(rut_limpio) >= 2:
                rut_limpio = rut_limpio[:-1] + '-' + rut_limpio[-1]
            
            # Buscar reservas activas y futuras
            ahora = timezone.now()
            reservas = Reserva.objects.filter(
                rut=rut_limpio,
                fecha_hora_fin__gte=ahora
            ).order_by('-fecha_hora_inicio')
            
            if not reservas.exists():
                messages.info(request, 'No se encontraron reservas activas con este RUT.')
    
    context = {
        'reservas': reservas,
        'rut_buscado': rut_buscado,
    }
    return render(request, 'salas/mis_reservas.html', context)
