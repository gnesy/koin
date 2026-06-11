from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UsuarioManager(BaseUserManager):
    def create_user(self, correo_usuario, nombre_usuario, apellido_usuario, nombre_familia_usuario, password=None):
        if not correo_usuario:
            raise ValueError('El usuario debe tener un correo electrónico')
        
        user = self.model(
            correo_usuario=self.normalize_email(correo_usuario),
            nombre_usuario=nombre_usuario,
            apellido_usuario=apellido_usuario,
            nombre_familia_usuario=nombre_familia_usuario,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo_usuario, nombre_usuario, apellido_usuario, nombre_familia_usuario, password=None):
        user = self.create_user(
            correo_usuario,
            nombre_usuario=nombre_usuario,
            apellido_usuario=apellido_usuario,
            nombre_familia_usuario=nombre_familia_usuario,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Usuario(AbstractBaseUser, PermissionsMixin):
    correo_usuario = models.EmailField(unique=True, max_length=255)
    nombre_usuario = models.CharField(max_length=100)
    apellido_usuario = models.CharField(max_length=100)
    nombre_familia_usuario = models.CharField(max_length=150)
    # ... tus campos anteriores de Usuario (correo, nombre, etc) ...

    # 1. Definimos las 3 preguntas predeterminadas
    PREGUNTAS_CHOICES = [
        ('mascota', '¿Cuál fue el nombre de tu primera mascota?'),
        ('ciudad', '¿En qué ciudad nació tu madre?'),
        ('apodo', '¿Cuál era tu apodo en la infancia?'),
    ]
    
    # 2. Agregamos los dos campos nuevos al usuario
    pregunta_seguridad = models.CharField(max_length=20, choices=PREGUNTAS_CHOICES, default='mascota')
    respuesta_seguridad = models.CharField(max_length=150, default='')

    # ... el resto de tu clase Usuario (objects, USERNAME_FIELD, Meta, etc) ...
    
    # Campos obligatorios para el funcionamiento de Django Admin
    # is_active = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo_usuario'
    REQUIRED_FIELDS = ['nombre_usuario', 'apellido_usuario', 'nombre_familia_usuario']

    class Meta:
        db_table = 'usuarios' # Nombre de la tabla en la base de datos

    def __str__(self):
        return f"{self.correo_usuario} - {self.nombre_familia_usuario}"

# Tabla de Monedas
class Moneda(models.Model):
    codigo = models.CharField(max_length=5, unique=True) # Ej: USD, VES
    nombre_moneda = models.CharField(max_length=50)

    def __str__(self):
        return self.codigo

# Tabla de Cuentas
class Cuenta(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT)
    nombre_cuenta = models.CharField(max_length=100)
    saldo_inicial_cuenta = models.DecimalField(max_digits=15, decimal_places=2)
    color_cuenta = models.CharField(max_length=20, help_text="Código hexadecimal o nombre del color")

    def __str__(self):
        return f"{self.nombre_cuenta} | Saldo disponible: {self.saldo_inicial_cuenta} {self.moneda.codigo}"

# Tabla de Categorías
class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=100)
    tipo_categoria = models.CharField(max_length=50) # Ej: Alimentación, Servicios

    def __str__(self):
        return self.nombre_categoria

# Tabla de Tipo de Movimiento
class TipoMovimiento(models.Model):
    nombre_movimiento = models.CharField(max_length=50) # Ej: Ingreso, Egreso, Transferencia

    def __str__(self):
        return self.nombre_movimiento

# Tabla de Movimientos (Transacciones)
class Movimiento(models.Model):
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    tipo_movimiento = models.ForeignKey(TipoMovimiento, on_delete=models.PROTECT)
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT)
    cantidad_moneda = models.DecimalField(max_digits=15, decimal_places=2)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.cantidad_moneda}"
    
