from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils import timezone
from django import forms

from .models import (
    Cuenta, 
    Moneda, 
    Usuario, 
    Movimiento, 
    Categoria
)

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Correo electrónico',
            'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors',
            'type': 'email' 
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
            'id': 'password_id',
            'placeholder': 'Contraseña',
            'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'
        }),
        help_text="<ul><li>No uses información personal.</li><li>Mínimo 8 caracteres.</li><li>No uses claves comunes.</li><li>No puede ser solo números.</li></ul>"
    )
    
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id': 'confirmar_password_id',
            'placeholder': 'Confirmar contraseña',
            'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'
        })
    )

    class Meta:
        model = Usuario
        # Añadimos pregunta y respuesta al registro
        fields = ['nombre_usuario', 'apellido_usuario', 'nombre_familia_usuario', 'correo_usuario', 'pregunta_seguridad', 'respuesta_seguridad']
        
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={'placeholder': 'Nombre', 'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'}),
            'apellido_usuario': forms.TextInput(attrs={'placeholder': 'Apellido', 'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'}),
            'nombre_familia_usuario': forms.TextInput(attrs={'placeholder': 'Nombre de la familia', 'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'}),
            'correo_usuario': forms.EmailInput(attrs={'placeholder': 'Correo electrónico', 'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'}),
            'pregunta_seguridad': forms.Select(attrs={'class': 'w-full pl-4 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'}),
            'respuesta_seguridad': forms.TextInput(attrs={'placeholder': 'Escribe tu respuesta secreta', 'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'}),
        }

    # Validamos que la respuesta se guarde SIEMPRE en minúsculas y sin espacios extra 
    # para que el usuario no se equivoque al recuperar la clave si usa mayúsculas.
    def clean_respuesta_seguridad(self):
        respuesta = self.cleaned_data.get('respuesta_seguridad')
        if respuesta:
            return respuesta.strip().lower()
        return respuesta

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmar_password = cleaned_data.get("confirmar_password")
        correo_usuario = cleaned_data.get("correo_usuario")

        if password and confirmar_password and password != confirmar_password:
            self.add_error('confirmar_password', "Las contraseñas no coinciden.")

        if password:
            usuario_temporal = Usuario(
                nombre_usuario=cleaned_data.get('nombre_usuario'),
                apellido_usuario=cleaned_data.get('apellido_usuario'),
                correo_usuario=correo_usuario
            )
            try:
                password_validation.validate_password(password, usuario_temporal)
            except ValidationError as error:
                self.add_error('password', error)
            
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class RecuperarCorreoForm(forms.Form):
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Correo electrónico registrado',
            'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors',
        })
    )

class RecuperarRespuestaForm(forms.Form):
    respuesta = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Tu respuesta secreta',
            'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors text-center font-bold text-charcoal-teal',
        })
    )
    
    def clean_respuesta(self):
        respuesta = self.cleaned_data.get('respuesta')
        if respuesta:
            return respuesta.strip().lower() # Convertimos a minúscula para comparar exacto
        return respuesta

class CuentaForm(forms.ModelForm):
    moneda = forms.ModelChoiceField(
        queryset=Moneda.objects.all(),
        empty_label="Seleccione la moneda",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors',
            'required': 'true'
        })
    )

    class Meta:
        model = Cuenta
        fields = ['nombre_cuenta', 'moneda', 'saldo_inicial_cuenta', 'color_cuenta']
        
        widgets = {
            'nombre_cuenta': forms.TextInput(attrs={
                'placeholder': 'Ej: Cuenta Nómina, Ahorros', 
                'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors',
                'maxlength': '50',
                'required': 'true'
            }),
            'saldo_inicial_cuenta': forms.NumberInput(attrs={
                'placeholder': '0.00', 
                'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors', 
                'step': '0.01',
                'min': '0'
            }),
            # MODIFICACIÓN: Ocultamos el campo tradicional y le damos el color oscuro por defecto
            'color_cuenta': forms.TextInput(attrs={
                'type': 'hidden',
                'value': '#16232C'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['saldo_inicial_cuenta'].required = False

    def clean_saldo_inicial_cuenta(self):
        saldo = self.cleaned_data.get('saldo_inicial_cuenta')
        if saldo is None:
            return 0.00
        return saldo
    moneda = forms.ModelChoiceField(
        queryset=Moneda.objects.all(),
        empty_label="Seleccione la moneda",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors',
            'required': 'true'
        })
    )

    class Meta:
        model = Cuenta
        fields = ['nombre_cuenta', 'moneda', 'saldo_inicial_cuenta', 'color_cuenta']
        
        widgets = {
            'nombre_cuenta': forms.TextInput(attrs={
                'placeholder': 'Ej: Cuenta Nómina, Ahorros', 
                'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors',
                'maxlength': '50',
                'required': 'true'
            }),
            'saldo_inicial_cuenta': forms.NumberInput(attrs={
                'placeholder': '0.00', 
                'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors', 
                'step': '0.01',
                'min': '0'
            }),
            'color_cuenta': forms.TextInput(attrs={
                'type': 'color', 
                'class': 'w-full h-12 px-2 py-1 bg-pale-blue-grey rounded-xl outline-none cursor-pointer'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['saldo_inicial_cuenta'].required = False

    def clean_saldo_inicial_cuenta(self):
        saldo = self.cleaned_data.get('saldo_inicial_cuenta')
        if saldo is None:
            return 0.00
        return saldo

class IngresoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['cuenta', 'categoria', 'cantidad_moneda', 'fecha_creacion', 'descripcion']
        widgets = {
            'fecha_creacion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['cuenta'].queryset = Cuenta.objects.filter(usuario=user)

        self.fields['categoria'].queryset = Categoria.objects.filter(tipo_categoria='ingreso')

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors border border-transparent focus:border-mint-green group-hover:border-[#05060f]'
            })
            
        self.fields['cantidad_moneda'].widget.attrs.update({
            'placeholder': '0.00', 
            'step': '0.01',
            'min': '0.01',
            'required': 'true'
        })
        self.fields['descripcion'].widget.attrs.update({'rows': 3, 'placeholder': 'Ej: Quincena, Venta de tortas, etc.', 'maxlength': '150'})

    def clean_cantidad_moneda(self):
        cantidad = self.cleaned_data.get('cantidad_moneda')
        if cantidad is None or cantidad <= 0:
            raise ValidationError("El monto debe ser mayor a 0.")
        return cantidad

    def clean_fecha_creacion(self):
        fecha = self.cleaned_data.get('fecha_creacion')
        if fecha and fecha > timezone.now():
            raise ValidationError("No puedes registrar un movimiento con fecha en el futuro.")
        return fecha

class GastoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['cuenta', 'categoria', 'cantidad_moneda', 'fecha_creacion', 'descripcion']
        widgets = {
            'fecha_creacion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['cuenta'].queryset = Cuenta.objects.filter(usuario=user)

        self.fields['categoria'].queryset = Categoria.objects.filter(tipo_categoria='gasto')

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors border border-transparent focus:border-red-400 group-hover:border-[#05060f]'
            })
            
        self.fields['cantidad_moneda'].widget.attrs.update({
            'placeholder': '0.00', 
            'step': '0.01',
            'min': '0.01',
            'required': 'true'
        })
        self.fields['descripcion'].widget.attrs.update({'rows': 3, 'placeholder': 'Ej: Mercado semanal, Factura de luz, etc.', 'maxlength': '150'})

    def clean_cantidad_moneda(self):
        cantidad = self.cleaned_data.get('cantidad_moneda')
        if cantidad is None or cantidad <= 0:
            raise ValidationError("El monto debe ser mayor a 0.")
        return cantidad

    def clean_fecha_creacion(self):
        fecha = self.cleaned_data.get('fecha_creacion')
        if fecha and fecha > timezone.now():
            raise ValidationError("No puedes registrar un movimiento con fecha en el futuro.")
        return fecha
    
class TransferenciaForm(forms.ModelForm):
    cuenta_destino = forms.ModelChoiceField(
        queryset=Cuenta.objects.none(),
        empty_label="Selecciona cuenta destino",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors border border-transparent focus:border-gray-400 group-hover:border-[#05060f]'
        })
    )

    class Meta:
        model = Movimiento
        fields = ['cuenta', 'cantidad_moneda', 'fecha_creacion', 'descripcion']
        widgets = {
            'fecha_creacion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['cuenta'].queryset = Cuenta.objects.filter(usuario=user)
            self.fields['cuenta'].label = "¿Desde qué cuenta sale el dinero?"
            self.fields['cuenta_destino'].queryset = Cuenta.objects.filter(usuario=user)
            self.fields['cuenta_destino'].label = "¿A qué cuenta ingresa el dinero?"

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors border border-transparent focus:border-gray-400 group-hover:border-[#05060f]'
            })

        self.fields['cantidad_moneda'].widget.attrs.update({
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0.01',
            'required': 'true'
        })
        self.fields['descripcion'].widget.attrs.update({'rows': 3, 'placeholder': 'Ej: Traspaso a ahorros, etc.', 'maxlength': '150'})

    def clean_cantidad_moneda(self):
        cantidad = self.cleaned_data.get('cantidad_moneda')
        if cantidad is None or cantidad <= 0:
            raise ValidationError("El monto debe ser mayor a 0.")
        return cantidad

    def clean_fecha_creacion(self):
        fecha = self.cleaned_data.get('fecha_creacion')
        if fecha and fecha > timezone.now():
            raise ValidationError("No puedes registrar un movimiento con fecha en el futuro.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        cuenta_origen = cleaned_data.get("cuenta")
        cuenta_destino = cleaned_data.get("cuenta_destino")

        if cuenta_origen and cuenta_destino and cuenta_origen == cuenta_destino:
            self.add_error('cuenta_destino', "La cuenta de destino no puede ser la misma que la de origen.")
            
        if cuenta_origen and cuenta_destino and cuenta_origen.moneda != cuenta_destino.moneda:
            self.add_error('cuenta_destino', f"Incompatible: No puedes transferir de una cuenta en {cuenta_origen.moneda.codigo} a una en {cuenta_destino.moneda.codigo}.")

        return cleaned_data

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre_usuario', 'apellido_usuario', 'nombre_familia_usuario', 'correo_usuario']
        
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors border border-transparent focus:border-mint-green'}),
            'apellido_usuario': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors border border-transparent focus:border-mint-green'}),
            'nombre_familia_usuario': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors border border-transparent focus:border-mint-green'}),
            'correo_usuario': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors border border-transparent focus:border-mint-green'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors border border-transparent focus:border-mint-green'
            })

class RestablecerPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Nueva contraseña',
            'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'
        })
    )
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirmar nueva contraseña',
            'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmar_password = cleaned_data.get("confirmar_password")

        if password and confirmar_password and password != confirmar_password:
            self.add_error('confirmar_password', "Las contraseñas no coinciden.")
        return cleaned_data
    
class CambiarPreguntaSeguridadForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['pregunta_seguridad', 'respuesta_seguridad']
        
        widgets = {
            'pregunta_seguridad': forms.Select(attrs={
                'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'
            }),
            'respuesta_seguridad': forms.TextInput(attrs={
                'placeholder': 'Escribe tu nueva respuesta secreta', 
                'class': 'w-full pl-12 pr-4 py-3 bg-pale-blue-grey rounded-full outline-none transition-colors'
            }),
        }

    def clean_respuesta_seguridad(self):
        respuesta = self.cleaned_data.get('respuesta_seguridad')
        if respuesta:
            return respuesta.strip().lower()
        return respuesta