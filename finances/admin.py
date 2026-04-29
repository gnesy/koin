from django.contrib import admin
from .models import PerfilFamilia, Moneda, Cuenta, Categoria, TipoMovimiento, Movimiento

# Registramos los modelos básicos
admin.site.register(PerfilFamilia)
admin.site.register(Moneda)
admin.site.register(Cuenta)
admin.site.register(Categoria)
admin.site.register(TipoMovimiento)

# Un pequeño truco para que los movimientos se vean mejor en el panel
@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('cuenta', 'tipo_movimiento', 'cantidad_moneda', 'fecha_creacion')
    list_filter = ('tipo_movimiento', 'cuenta')