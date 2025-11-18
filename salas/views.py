from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Sala, Reserva
from .forms import ReservaForm
from django.contrib.auth import authenticate, login, logout

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

# Verificar si el usuario es staff (administrador)
def es_administrador(user):
    return user.is_staff

@login_required
@user_passes_test(es_administrador)
def panel_admin(request):
    """
    Panel de administración personalizado
    """
    # Estadísticas generales
    total_salas = Sala.objects.count()
    salas_habilitadas = Sala.objects.filter(habilitada=True).count()
    salas_deshabilitadas = total_salas - salas_habilitadas
    
    ahora = timezone.now()
    total_reservas = Reserva.objects.count()
    reservas_activas = Reserva.objects.filter(fecha_hora_fin__gte=ahora).count()
    reservas_finalizadas = total_reservas - reservas_activas
    
    # Últimas reservas
    ultimas_reservas = Reserva.objects.all().order_by('-fecha_creacion')[:10]
    
    context = {
        'total_salas': total_salas,
        'salas_habilitadas': salas_habilitadas,
        'salas_deshabilitadas': salas_deshabilitadas,
        'total_reservas': total_reservas,
        'reservas_activas': reservas_activas,
        'reservas_finalizadas': reservas_finalizadas,
        'ultimas_reservas': ultimas_reservas,
    }
    return render(request, 'admin/panel_admin.html', context)

@login_required
@user_passes_test(es_administrador)
def admin_salas(request):
    """
    Gestión de salas desde el panel personalizado
    """
    salas = Sala.objects.all().order_by('nombre')
    
    context = {
        'salas': salas,
    }
    return render(request, 'admin/admin_salas.html', context)

@login_required
@user_passes_test(es_administrador)
def admin_crear_sala(request):
    """
    Crear una nueva sala desde el panel personalizado
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        capacidad = request.POST.get('capacidad')
        descripcion = request.POST.get('descripcion', '')
        habilitada = request.POST.get('habilitada') == 'on'
        
        try:
            Sala.objects.create(
                nombre=nombre,
                capacidad=capacidad,
                descripcion=descripcion,
                habilitada=habilitada
            )
            messages.success(request, f'Sala "{nombre}" creada exitosamente.')
            return redirect('admin_salas')
        except Exception as e:
            messages.error(request, f'Error al crear la sala: {str(e)}')
    
    return render(request, 'admin/admin_crear_sala.html')

@login_required
@user_passes_test(es_administrador)
def admin_editar_sala(request, sala_id):
    """
    Editar una sala existente desde el panel personalizado
    """
    sala = get_object_or_404(Sala, id=sala_id)
    
    if request.method == 'POST':
        sala.nombre = request.POST.get('nombre')
        sala.capacidad = request.POST.get('capacidad')
        sala.descripcion = request.POST.get('descripcion', '')
        sala.habilitada = request.POST.get('habilitada') == 'on'
        
        try:
            sala.save()
            messages.success(request, f'Sala "{sala.nombre}" actualizada exitosamente.')
            return redirect('admin_salas')
        except Exception as e:
            messages.error(request, f'Error al actualizar la sala: {str(e)}')
    
    context = {'sala': sala}
    return render(request, 'admin/admin_editar_sala.html', context)

@login_required
@user_passes_test(es_administrador)
def admin_eliminar_sala(request, sala_id):
    """
    Eliminar una sala desde el panel personalizado
    """
    sala = get_object_or_404(Sala, id=sala_id)
    
    if request.method == 'POST':
        nombre_sala = sala.nombre
        sala.delete()
        messages.success(request, f'Sala "{nombre_sala}" eliminada exitosamente.')
        return redirect('admin_salas')
    
    context = {'sala': sala}
    return render(request, 'admin/admin_eliminar_sala.html', context)

@login_required
@user_passes_test(es_administrador)
def admin_reservas(request):
    """
    Gestión de reservas desde el panel personalizado
    """
    reservas = Reserva.objects.all().order_by('-fecha_creacion')
    
    context = {
        'reservas': reservas,
    }
    return render(request, 'admin/admin_reservas.html', context)

@login_required
@user_passes_test(es_administrador)
def admin_eliminar_reserva(request, reserva_id):
    """
    Eliminar una reserva desde el panel personalizado
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    if request.method == 'POST':
        reserva.delete()
        messages.success(request, 'Reserva eliminada exitosamente.')
        return redirect('admin_reservas')
    
    context = {'reserva': reserva}
    return render(request, 'admin/admin_eliminar_reserva.html', context)


def login_view(request):
    """
    Vista de login personalizada para el panel de administración
    """
    if request.user.is_authenticated:
        return redirect('panel_admin')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'panel_admin')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'salas/login.html')

def logout_view(request):
    """
    Vista de logout personalizada para el panel de administración
    """
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('lista_salas')
