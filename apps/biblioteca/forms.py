from django import forms
from .models import Biblioteca

class ContenidoForm(forms.ModelForm):
    class Meta:
        model = Biblioteca
        fields = ['titulo', 'descripcion', 'tipo', 'nivel', 'activo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el título del contenido'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ingrese una descripción detallada'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar etiquetas
        self.fields['titulo'].label = 'Título del Contenido'
        self.fields['descripcion'].label = 'Descripción Detallada'
        self.fields['tipo'].label = 'Tipo de Contenido'
        self.fields['nivel'].label = 'Nivel de Dificultad'
        self.fields['activo'].label = '¿Está activo?'
        
        # Agregar clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            if field_name != 'activo':  # No aplicar a los checkboxes
                field.widget.attrs.update({'class': 'form-control'})
