from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Reserva, Sala

class ReservaForm(forms.ModelForm):
    """
    Formulario para crear o actualizar una reserva de sala.
    """
    class Meta:
        model = Reserva
        fields = ['sala', 'rut', 'nombre_reservante']
        widgets = {
            'sala': forms.Select(attrs={
                'class': 'form-control',
            }),
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12345678-9',
                'maxlength': '12',
            }),
            'nombre_reservante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su nombre completo',
            }),
        }
        labels = {
            'sala': 'Seleccione una sala',
            'rut': 'RUT (con guión)',
            'nombre_reservante': 'Nombre completo',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo salas habilitadas y disponibles
        self.fields['sala'].queryset = Sala.objects.filter(habilitada=True)
    
    def clean_rut(self):
        """
        Limpia y valida el formato del RUT
        """
        rut = self.cleaned_data.get('rut')
        if rut:
            # Eliminar puntos y espacios
            rut = rut.replace('.', '').replace(' ', '').upper()
            # Agregar guión si no lo tiene
            if '-' not in rut and len(rut) >= 2:
                rut = rut[:-1] + '-' + rut[-1]
        return rut
    
    def clean_sala(self):
        """
        Se valida que la sala esté disponible
        """
        sala = self.cleaned_data.get('sala')
        if sala and not sala.esta_disponible():
            raise ValidationError('Esta sala no está disponible en este momento.')
        return sala
