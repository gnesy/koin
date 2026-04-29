from django import forms
from .models import Usuario
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    # El campo se llama 'username' internamente para Django, pero lo configuramos como email visualmente
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Correo electrónico',
            'class': 'w-full pl-12 pr-4 py-3 bg-white border border-gray-200 rounded-full focus:outline-none focus:border-koin-dark focus:ring-1 focus:ring-koin-dark transition-colors',
            'type': 'email' # Forzamos el teclado de correo en móviles
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'w-full pl-12 pr-12 py-3 bg-white border border-gray-200 rounded-full focus:outline-none focus:border-koin-dark focus:ring-1 focus:ring-koin-dark transition-colors'
        })
    )

class RegistroUsuarioForm(forms.ModelForm):
    # Definimos la contraseña manualmente para asegurarnos de que se oculte al escribir
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Crear contraseña',
            'class': 'w-full pl-12 pr-4 py-3 bg-white border border-gray-200 rounded-full focus:outline-none focus:border-koin-dark focus:ring-1 focus:ring-koin-dark transition-colors'
        })
    )

    class Meta:
        model = Usuario
        # Usamos exactamente los nombres de los campos de tu nuevo modelo
        fields = ['nombre_usuario', 'apellido_usuario', 'nombre_familia_usuario', 'correo_usuario']
        
        # Inyectamos tus clases de Tailwind a cada campo generado por el modelo
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={'placeholder': 'Nombre de jefe de familia', 'class': 'w-full pl-12 pr-4 py-3 bg-white border border-gray-200 rounded-full focus:outline-none focus:border-koin-dark focus:ring-1 focus:ring-koin-dark transition-colors'}),
            'apellido_usuario': forms.TextInput(attrs={'placeholder': 'Apellido de jefe de familia', 'class': 'w-full pl-12 pr-4 py-3 bg-white border border-gray-200 rounded-full focus:outline-none focus:border-koin-dark focus:ring-1 focus:ring-koin-dark transition-colors'}),
            'nombre_familia_usuario': forms.TextInput(attrs={'placeholder': 'Nombre de familia', 'class': 'w-full pl-12 pr-4 py-3 bg-white border border-gray-200 rounded-full focus:outline-none focus:border-koin-dark focus:ring-1 focus:ring-koin-dark transition-colors'}),
            'correo_usuario': forms.EmailInput(attrs={'placeholder': 'Correo electrónico', 'class': 'w-full pl-12 pr-4 py-3 bg-white border border-gray-200 rounded-full focus:outline-none focus:border-koin-dark focus:ring-1 focus:ring-koin-dark transition-colors'}),
        }

    def save(self, commit=True):
        # Interceptamos el guardado para encriptar la contraseña de forma segura
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user