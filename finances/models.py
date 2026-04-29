from django.db import models

from django.db import models
from django.contrib.auth.models import User

# Extensión del usuario para el Jefe de Familia
class PerfilFamilia(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nombre_familia = models.CharField(max_length=100)

    def __str__(self):
        return f"Familia {self.nombre_familia}"

# Tabla de Monedas
class Moneda(models.Model):
    codigo = models.CharField(max_length=5, unique=True) # Ej: USD, VES
    nombre_moneda = models.CharField(max_length=50)
    tasa_cambio = models.DecimalField(max_digits=18, decimal_places=4)

    def __str__(self):
        return self.nombre_moneda

# Tabla de Cuentas
class Cuenta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT)
    nombre_cuenta = models.CharField(max_length=100)
    saldo_inicial_cuenta = models.DecimalField(max_digits=15, decimal_places=2)
    color_cuenta = models.CharField(max_length=20, help_text="Código hexadecimal o nombre del color")

    def __str__(self):
        return f"{self.nombre_cuenta} ({self.usuario.username})"

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
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.cantidad_moneda}"
