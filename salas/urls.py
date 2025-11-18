from django.urls import path
from . import views

urlpatterns = [
    # URLs públicas
    path('', views.lista_salas, name='lista_salas'),
    path('sala/<int:sala_id>/', views.detalle_sala, name='detalle_sala'),
    path('sala/<int:sala_id>/reservar/', views.crear_reserva, name='crear_reserva'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),

    # URLs de autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # URLs del panel de administración personalizado
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('panel-admin/salas/', views.admin_salas, name='admin_salas'),
    path('panel-admin/salas/crear/', views.admin_crear_sala, name='admin_crear_sala'),
    path('panel-admin/salas/<int:sala_id>/editar/', views.admin_editar_sala, name='admin_editar_sala'),
    path('panel-admin/salas/<int:sala_id>/eliminar/', views.admin_eliminar_sala, name='admin_eliminar_sala'),
    path('panel-admin/reservas/', views.admin_reservas, name='admin_reservas'),
    path('panel-admin/reservas/<int:reserva_id>/eliminar/', views.admin_eliminar_reserva, name='admin_eliminar_reserva'),
    path('panel-admin/reservas/<int:reserva_id>/finalizar/', views.admin_finalizar_reserva, name='admin_finalizar_reserva'),
]
