"""
URL configuration for koin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from finances.views import registro_usuario, dashboard, login_view, cuentas_view, editar_cuenta_view, eliminar_cuenta_view, ingreso_view, gasto_view, historial_movimientos_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('panel-financiero/', dashboard, name='dashboard'),
    path('iniciar-sesion/', login_view, name='login'),
    path('registro/', registro_usuario, name='registro'),
    path('cuentas/', cuentas_view, name='cuentas'),
    path("salir/", LogoutView.as_view(next_page="login"), name="logout"),
    path('cuentas/editar/<int:cuenta_id>/', editar_cuenta_view, name='editar_cuenta'),
    path('cuentas/eliminar/<int:cuenta_id>/', eliminar_cuenta_view, name='eliminar_cuenta'),
    path('movimientos/add-ingreso/', ingreso_view, name='registrar_ingreso'),
    path('movimientos/add-gasto/', gasto_view, name='registrar_gasto'),
    path('movimientos/', historial_movimientos_view, name='historial_movimientos'),
]
