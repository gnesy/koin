from django import forms
from .models import Usuario
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    # El campo se llama 'username' internamente para Django, pero lo configuramos como email visualmente
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Correo electrónico',
            'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors',
            'type': 'email' # Forzamos el teclado de correo en móviles
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'w-full pl-12 pr-12 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'
        })
    )

class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'
        })
    )
    
    # NUEVO: Campo para confirmar contraseña
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirmar contraseña',
            'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'
        })
    )

    class Meta:
        model = Usuario
        fields = ['nombre_usuario', 'apellido_usuario', 'nombre_familia_usuario', 'correo_usuario']
        
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={'placeholder': 'Nombre de jefe de familia', 'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'}),
            'apellido_usuario': forms.TextInput(attrs={'placeholder': 'Apellido del jefe de familia', 'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'}),
            'nombre_familia_usuario': forms.TextInput(attrs={'placeholder': 'Nombre de la familia', 'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'}),
            'correo_usuario': forms.EmailInput(attrs={'placeholder': 'Correo electrónico', 'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'}),
        }

    # NUEVO: Validación para que las contraseñas coincidan
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmar_password = cleaned_data.get("confirmar_password")

        if password and confirmar_password and password != confirmar_password:
            self.add_error('confirmar_password', "Las contraseñas no coinciden.")
            
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user