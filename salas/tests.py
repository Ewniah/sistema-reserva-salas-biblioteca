from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Sala, Reserva, validar_rut
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class ValidacionRUTTestCase(TestCase):
    """
    Tests para la validación de RUT chileno con módulo 11
    """
    
    def test_rut_valido_con_numero(self):
        """Test con RUT válido que tiene dígito verificador numérico"""
        try:
            validar_rut('11111111-1')
            validar_rut('12345678-5')
        except ValidationError:
            self.fail("La validación de RUT falló con un RUT válido")
    
    def test_rut_valido_con_k(self):
        """Test con RUT válido que tiene K como dígito verificador"""
        try:
            # Usar un RUT que realmente tenga K como verificador
            validar_rut('9564175-K')
        except ValidationError as e:
            self.fail("La validación de RUT falló con K válida Error: {e}")
    
    def test_rut_invalido_digito_verificador(self):
        """Test con RUT inválido (dígito verificador incorrecto)"""
        with self.assertRaises(ValidationError):
            validar_rut('12345678-0')
    
    def test_rut_muy_corto(self):
        """Test con RUT demasiado corto"""
        with self.assertRaises(ValidationError):
            validar_rut('1-1')
    
    def test_rut_con_letras_en_cuerpo(self):
        """Test con RUT que tiene letras en el cuerpo"""
        with self.assertRaises(ValidationError):
            validar_rut('1234567A-5')


class SalaModelTestCase(TestCase):
    """
    Tests para el modelo Sala
    """
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.sala = Sala.objects.create(
            nombre='Sala de Prueba',
            capacidad=10,
            descripcion='Sala para testing',
            habilitada=True
        )
    
    def test_creacion_sala(self):
        """Test para verificar que se crea correctamente una sala"""
        self.assertEqual(self.sala.nombre, 'Sala de Prueba')
        self.assertEqual(self.sala.capacidad, 10)
        self.assertTrue(self.sala.habilitada)
    
    def test_sala_disponible_sin_reservas(self):
        """Test para verificar que una sala sin reservas está disponible"""
        self.assertTrue(self.sala.esta_disponible())
    
    def test_sala_disponible_con_reserva_activa(self):
        """Test para verificar que una sala con reserva activa no está disponible"""
        ahora = timezone.now()
        Reserva.objects.create(
            sala=self.sala,
            rut='11111111-1',
            nombre_reservante='Test User',
            fecha_hora_inicio=ahora,
            fecha_hora_fin=ahora + timedelta(hours=2)
        )
        self.assertFalse(self.sala.esta_disponible())
    
    def test_sala_disponible_con_reserva_pasada(self):
        """Test para verificar que una sala con reserva pasada está disponible"""
        pasado = timezone.now() - timedelta(hours=3)
        Reserva.objects.create(
            sala=self.sala,
            rut='11111111-1',
            nombre_reservante='Test User',
            fecha_hora_inicio=pasado,
            fecha_hora_fin=pasado + timedelta(hours=2)
        )
        self.assertTrue(self.sala.esta_disponible())
    
    def test_sala_deshabilitada_no_disponible(self):
        """Test para verificar que una sala deshabilitada no está disponible"""
        self.sala.habilitada = False
        self.sala.save()
        self.assertFalse(self.sala.esta_disponible())


class ReservaModelTestCase(TestCase):
    """
    Tests para el modelo Reserva
    """
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.sala = Sala.objects.create(
            nombre='Sala Test',
            capacidad=5,
            habilitada=True
        )
    
    def test_creacion_reserva_automatica(self):
        """Test para verificar que se asignan fechas automáticamente"""
        ahora = timezone.now()
        reserva = Reserva.objects.create(
            sala=self.sala,
            rut='11111111-1',
            nombre_reservante='Juan Pérez'
        )
        
        # Verificar que se asignaron las fechas
        self.assertIsNotNone(reserva.fecha_hora_inicio)
        self.assertIsNotNone(reserva.fecha_hora_fin)
        
        # Verificar que la duración es de 2 horas
        duracion = reserva.fecha_hora_fin - reserva.fecha_hora_inicio
        self.assertEqual(duracion, timedelta(hours=2))
    
    def test_validacion_rut_en_reserva(self):
        """Test para verificar que se valida el RUT al crear una reserva"""
        with self.assertRaises(ValidationError):
            ahora = timezone.now()
            reserva = Reserva(
                sala=self.sala,
                rut='12345678-0',  # RUT inválido
                nombre_reservante='Test User',
                fecha_hora_inicio=ahora,
                fecha_hora_fin=ahora + timedelta(hours=2)
            )
            reserva.full_clean()
    
    def test_restriccion_una_reserva_por_rut(self):
        """Test para verificar que un RUT no puede tener dos reservas activas"""
        ahora = timezone.now()
        
        # Crear primera reserva
        Reserva.objects.create(
            sala=self.sala,
            rut='11111111-1',
            nombre_reservante='Juan Pérez',
            fecha_hora_inicio=ahora,
            fecha_hora_fin=ahora + timedelta(hours=2)
        )
        
        # Crear otra sala
        sala2 = Sala.objects.create(
            nombre='Sala Test 2',
            capacidad=5,
            habilitada=True
        )
        
        # Intentar crear segunda reserva con el mismo RUT
        with self.assertRaises(ValidationError):
            reserva2 = Reserva(
                sala=sala2,
                rut='11111111-1',
                nombre_reservante='Juan Pérez',
                fecha_hora_inicio=ahora,
                fecha_hora_fin=ahora + timedelta(hours=2)
            )
            reserva2.full_clean()
    
    def test_validacion_sala_habilitada(self):
        """Test para verificar que no se puede reservar una sala deshabilitada"""
        self.sala.habilitada = False
        self.sala.save()
        
        ahora = timezone.now()
        with self.assertRaises(ValidationError):
            reserva = Reserva(
                sala=self.sala,
                rut='11111111-1',
                nombre_reservante='Test User',
                fecha_hora_inicio=ahora,
                fecha_hora_fin=ahora + timedelta(hours=2)
            )
            reserva.full_clean()


class VistasPublicasTestCase(TestCase):
    """
    Tests para las vistas públicas del sistema
    """
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.sala = Sala.objects.create(
            nombre='Sala Pública',
            capacidad=10,
            habilitada=True
        )
    
    def test_lista_salas_view(self):
        """Test para verificar que la página de lista de salas funciona"""
        response = self.client.get(reverse('lista_salas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sala Pública')
    
    def test_detalle_sala_view(self):
        """Test para verificar que la página de detalle de sala funciona"""
        response = self.client.get(reverse('detalle_sala', args=[self.sala.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sala Pública')
    
    def test_crear_reserva_view_get(self):
        """Test para verificar que se muestra el formulario de reserva"""
        response = self.client.get(reverse('crear_reserva', args=[self.sala.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reservar')
    
    def test_crear_reserva_view_post_valido(self):
        """Test para crear una reserva con datos válidos"""
        response = self.client.post(reverse('crear_reserva', args=[self.sala.id]), {
            'sala': self.sala.id,
            'rut': '11111111-1',
            'nombre_reservante': 'Test User'
        })
        
        # Verificar que se creó la reserva
        self.assertEqual(Reserva.objects.count(), 1)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
    
    def test_crear_reserva_view_post_rut_invalido(self):
        """Test para crear una reserva con RUT inválido"""
        response = self.client.post(reverse('crear_reserva', args=[self.sala.id]), {
            'sala': self.sala.id,
            'rut': '12345678-0',  # RUT inválido
            'nombre_reservante': 'Test User'
        })
        
        # Verificar que no se creó la reserva
        self.assertEqual(Reserva.objects.count(), 0)


class VistasAdminTestCase(TestCase):
    """
    Tests para las vistas del panel de administración
    """
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        
        # Crear usuario administrador
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        
        # Crear sala de prueba
        self.sala = Sala.objects.create(
            nombre='Sala Admin Test',
            capacidad=10,
            habilitada=True
        )
    
    def test_panel_admin_requiere_login(self):
        """Test para verificar que el panel admin requiere login"""
        response = self.client.get(reverse('panel_admin'))
        self.assertEqual(response.status_code, 302)  # Redirección a login
    
    def test_panel_admin_con_login(self):
        """Test para verificar que el panel admin funciona con login"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('panel_admin'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Panel de Administración')
    
    def test_crear_sala_desde_panel(self):
        """Test para crear una sala desde el panel admin"""
        self.client.login(username='admin', password='admin123')
        
        response = self.client.post(reverse('admin_crear_sala'), {
            'nombre': 'Nueva Sala Test',
            'capacidad': 15,
            'descripcion': 'Sala creada en test',
            'habilitada': 'on'
        })
        
        # Verificar que se creó la sala
        self.assertEqual(Sala.objects.count(), 2)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
    
    def test_editar_sala_desde_panel(self):
        """Test para editar una sala desde el panel admin"""
        self.client.login(username='admin', password='admin123')
        
        response = self.client.post(reverse('admin_editar_sala', args=[self.sala.id]), {
            'nombre': 'Sala Editada',
            'capacidad': 20,
            'descripcion': 'Descripción editada',
            'habilitada': 'on'
        })
        
        # Verificar que se editó la sala
        self.sala.refresh_from_db()
        self.assertEqual(self.sala.nombre, 'Sala Editada')
        self.assertEqual(self.sala.capacidad, 20)
    
    def test_eliminar_sala_desde_panel(self):
        """Test para eliminar una sala desde el panel admin"""
        self.client.login(username='admin', password='admin123')
        
        response = self.client.post(reverse('admin_eliminar_sala', args=[self.sala.id]))
        
        # Verificar que se eliminó la sala
        self.assertEqual(Sala.objects.count(), 0)
    
    def test_finalizar_reserva_anticipadamente(self):
        """Test para finalizar una reserva antes de tiempo"""
        self.client.login(username='admin', password='admin123')
        
        # Crear una reserva
        ahora = timezone.now()
        reserva = Reserva.objects.create(
            sala=self.sala,
            rut='11111111-1',
            nombre_reservante='Test User',
            fecha_hora_inicio=ahora,
            fecha_hora_fin=ahora + timedelta(hours=2)
        )
        
        # Finalizar la reserva
        response = self.client.post(reverse('admin_finalizar_reserva', args=[reserva.id]))
        
        # Verificar que se finalizó
        reserva.refresh_from_db()
        self.assertLess(reserva.fecha_hora_fin, ahora + timedelta(hours=2))


class IntegracionTestCase(TestCase):
    """
    Tests de integración para flujos completos
    """
    
    def test_flujo_completo_reserva(self):
        """Test del flujo completo: crear sala, reservar, verificar disponibilidad"""
        # 1. Crear sala
        sala = Sala.objects.create(
            nombre='Sala Integración',
            capacidad=10,
            habilitada=True
        )
        
        # 2. Verificar que está disponible
        self.assertTrue(sala.esta_disponible())
        
        # 3. Crear reserva
        ahora = timezone.now()
        reserva = Reserva.objects.create(
            sala=sala,
            rut='11111111-1',
            nombre_reservante='Usuario Test',
            fecha_hora_inicio=ahora,
            fecha_hora_fin=ahora + timedelta(hours=2)
        )
        
        # 4. Verificar que ya no está disponible
        self.assertFalse(sala.esta_disponible())
        
        # 5. Finalizar la reserva (simular que pasó el tiempo)
        pasado = ahora - timedelta(hours=1)
        reserva.fecha_hora_inicio = pasado - timedelta(hours=2)
        reserva.fecha_hora_fin = pasado
        reserva.save(update_fields=['fecha_hora_inicio', 'fecha_hora_fin'])
        
        # 6. Verificar que vuelve a estar disponible
        self.assertTrue(sala.esta_disponible())
