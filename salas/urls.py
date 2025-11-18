from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_salas, name='lista_salas'),
    path('sala/<int:sala_id>/', views.detalle_sala, name='detalle_sala'),
    path('sala/<int:sala_id>/reservar/', views.crear_reserva, name='crear_reserva'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
]
