from django import forms
from .models import Cuenta, Moneda, Usuario, Movimiento, Categoria
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

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



class CuentaForm(forms.ModelForm):
    # Declaramos explícitamente el campo relacional
    moneda = forms.ModelChoiceField(
        queryset=Moneda.objects.all(), # Consulta todas las monedas en la base de datos
        empty_label="Moneda", # Opción por defecto
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors'
        })
    )

    class Meta:
        model = Cuenta
        fields = ['nombre_cuenta', 'moneda', 'saldo_inicial_cuenta', 'color_cuenta']
        
        # Como definimos 'moneda' arriba, la quitamos de este diccionario 'widgets'
        widgets = {
            'nombre_cuenta': forms.TextInput(attrs={
                'placeholder': 'Ej: Cuenta Nómina, Ahorros', 
                'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors'
            }),
            'saldo_inicial_cuenta': forms.NumberInput(attrs={
                'placeholder': '0.00', 
                'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors', 
                'step': '0.01'
            }),
            'color_cuenta': forms.TextInput(attrs={
                'type': 'color', 
                'class': 'w-full h-12 px-2 py-1 bg-pale-blue-grey rounded-xl outline-none cursor-pointer'
            }),
        }


class IngresoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        # 1. Agregamos la fecha de creación
        fields = ['cuenta', 'categoria', 'cantidad_moneda', 'fecha_creacion', 'descripcion']
        
        # 2. Forzamos el calendario nativo
        widgets = {
            'fecha_creacion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['cuenta'].queryset = Cuenta.objects.filter(usuario=user)

        self.fields['categoria'].queryset = Categoria.objects.filter(tipo_categoria='Ingreso')

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                # Agregamos el group-hover para la interactividad visual
                'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors border border-transparent focus:border-mint-green group-hover:border-[#05060f]'
            })
            
        # 3. Validación Frontend: Bloquea negativos
        self.fields['cantidad_moneda'].widget.attrs.update({
            'placeholder': '0.00', 
            'step': '0.01',
            'min': '0.01',
            'required': 'true'
        })
        self.fields['descripcion'].widget.attrs.update({'rows': 3, 'placeholder': 'Ej: Quincena, Venta de tortas, etc.'})

    # 4. Validación Backend: Protege el servidor
    def clean_cantidad_moneda(self):
        cantidad = self.cleaned_data.get('cantidad_moneda')
        if cantidad is None or cantidad <= 0:
            raise ValidationError("El monto debe ser mayor a 0.")
        return cantidad


class GastoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        # 1. Agregamos 'fecha_creacion' a la lista de campos
        fields = ['cuenta', 'categoria', 'cantidad_moneda', 'fecha_creacion', 'descripcion']
        
        # 2. Forzamos a que el input de fecha sea el calendario nativo del celular/navegador
        widgets = {
            'fecha_creacion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['cuenta'].queryset = Cuenta.objects.filter(usuario=user)

        self.fields['categoria'].queryset = Categoria.objects.filter(tipo_categoria='Gasto')

        # Aplicamos el diseño a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 bg-pale-blue-grey rounded-xl outline-none transition-colors border border-transparent focus:border-red-400 group-hover:border-[#05060f]'
            })
            
        # 3. Validación Frontend: min='0.01' bloquea los ceros y números negativos en el HTML
        self.fields['cantidad_moneda'].widget.attrs.update({
            'placeholder': '0.00', 
            'step': '0.01',
            'min': '0.01',
            'required': 'true'
        })
        self.fields['descripcion'].widget.attrs.update({'rows': 3, 'placeholder': 'Ej: Mercado semanal, Factura de luz, Condominio, etc.'})

    # 4. Validación Backend: Si alguien burla el HTML, el servidor de Django detiene el error aquí
    def clean_cantidad_moneda(self):
        cantidad = self.cleaned_data.get('cantidad_moneda')
        if cantidad is None or cantidad <= 0:
            raise ValidationError("El monto debe ser mayor a 0.")
        return cantidad