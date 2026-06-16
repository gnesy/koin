# Importaciones de librerías
from django.contrib.auth import login, update_session_auth_hash, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal as decimal
from django.contrib import messages
from django.db.models import Sum, Q
from django.db import transaction

# Importaciones locales
from finances.services import obtener_tasa_bcv_segura
from finances.forms import (
    RegistroUsuarioForm, 
    LoginForm, CuentaForm, 
    IngresoForm, 
    GastoForm, 
    TransferenciaForm, 
    EditarPerfilForm, 
    CustomPasswordChangeForm, 
    RestablecerPasswordForm, 
    RecuperarCorreoForm, 
    RecuperarRespuestaForm,
    CambiarPreguntaSeguridadForm
)
from finances.models import (
    Cuenta, 
    Movimiento, 
    TipoMovimiento, 
    Categoria, 
    Usuario
)

@login_required
def dashboard(request):
    usuario = request.user

    cuentas_del_usuario = Cuenta.objects.filter(usuario=usuario)

    suma_usd = cuentas_del_usuario.filter(moneda__codigo='USD').aggregate(total=Sum('saldo_inicial_cuenta'))['total']
    total_usd = round(suma_usd, 2) if suma_usd is not None else decimal("0.00")
    suma_ves = cuentas_del_usuario.filter(moneda__codigo='VES').aggregate(total=Sum('saldo_inicial_cuenta'))['total']
    total_ves = round(suma_ves, 2) if suma_ves is not None else decimal("0.00")

    # NUEVO: Cálculos matemáticos de conversión listos para enviar al HTML
    tasa_bcv = round(decimal(obtener_tasa_bcv_segura()), 2)
    usd_convertido_ves = round(total_usd * tasa_bcv, 2)
    ves_convertido_usd = round(total_ves / tasa_bcv, 2) if tasa_bcv > 0 else 0.00

    movimientos_recientes = Movimiento.objects.filter(cuenta__usuario=usuario).order_by('-fecha_creacion')[:3]

    contexto = {
        'cuentas': cuentas_del_usuario[:3],
        'total_cuentas': cuentas_del_usuario.count(),
        'familia' : usuario.nombre_familia_usuario,
        'nombre_completo' : f"{usuario.nombre_usuario} {usuario.apellido_usuario}",
        'total_usd': total_usd,
        'total_ves': total_ves,
        'usd_convertido_ves': usd_convertido_ves, # Se envía la conversión
        'ves_convertido_usd': ves_convertido_usd, # Se envía la conversión
        'tasa_bcv': tasa_bcv,
        'movimientos_recientes': movimientos_recientes,
    }

    return render(request, 'dashboard.html', contexto)
  
def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, "¡Tu cuenta ha sido creada exitosamente! Por favor, inicia sesión.")
            # AQUÍ ESTÁ LA MAGIA: Esta línea fuerza al navegador a ir al Login tras el éxito
            return redirect('login') 
        else:
            # PARA DEPURACIÓN: Si el formulario NO es válido, esto imprimirá en la 
            # terminal (donde corre tu servidor Django) la razón exacta del fallo.
            print("ERRORES EN EL REGISTRO:", form.errors)
    else:
        form = RegistroUsuarioForm()

    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect('dashboard')
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})

@login_required
def cuentas_view(request):
    mis_cuentas = Cuenta.objects.filter(usuario=request.user)
 
    if request.method == 'POST':
        form = CuentaForm(request.POST)
        if form.is_valid():
            nueva_cuenta = form.save(commit=False)
            nueva_cuenta.usuario = request.user
            nueva_cuenta.save()
            return redirect('cuentas') 
    else:
        form = CuentaForm()
    

    return render(request, 'cuentas.html', {
        'cuentas': mis_cuentas,
        'form': form,
    })

@login_required
def editar_cuenta_view(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, usuario=request.user)
    
    if request.method == 'POST':
        cuenta.nombre_cuenta = request.POST.get('nombre_cuenta')
        
        saldo = request.POST.get('saldo_inicial_cuenta')
        cuenta.saldo_inicial_cuenta = float(saldo) if saldo else 0.00
        
        cuenta.color_cuenta = request.POST.get('color_cuenta')
        cuenta.save()
        
    return redirect('cuentas')

@login_required
def eliminar_cuenta_view(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, usuario=request.user)
    
    if request.method == 'POST':
        cuenta.delete()
        
    return redirect('cuentas')

@login_required
def ingreso_view(request):
    tipo_ingreso, created = TipoMovimiento.objects.get_or_create(nombre_movimiento="Ingreso")

    if request.method == 'POST':
        form = IngresoForm(request.POST, user=request.user)
        
        if form.is_valid():
            with transaction.atomic():
                movimiento = form.save(commit=False)
                movimiento.tipo_movimiento = tipo_ingreso
                movimiento.moneda = movimiento.cuenta.moneda
                movimiento.save()

                cuenta_afectada = movimiento.cuenta
                cuenta_afectada.saldo_inicial_cuenta += movimiento.cantidad_moneda
                cuenta_afectada.save()

            return redirect('dashboard')
    else:
        form = IngresoForm(user=request.user)

    return render(request, 'ingreso.html', {'form': form})

@login_required
def gasto_view(request):
    tipo_gasto, created = TipoMovimiento.objects.get_or_create(nombre_movimiento="Gasto")

    if request.method == 'POST':
        form = GastoForm(request.POST, user=request.user)
        
        if form.is_valid():
            movimiento = form.save(commit=False)
            cuenta_afectada = movimiento.cuenta
            
            if cuenta_afectada.saldo_inicial_cuenta < movimiento.cantidad_moneda:
                messages.error(request, f"Saldo insuficiente. La cuenta {cuenta_afectada.nombre_cuenta} solo tiene {cuenta_afectada.saldo_inicial_cuenta}.")
                return render(request, 'gasto.html', {'form': form})

            with transaction.atomic():
                movimiento.tipo_movimiento = tipo_gasto
                movimiento.moneda = cuenta_afectada.moneda
                movimiento.save()

                cuenta_afectada.saldo_inicial_cuenta -= movimiento.cantidad_moneda
                cuenta_afectada.save()

            return redirect('dashboard')
    else:
        form = GastoForm(user=request.user)

    return render(request, 'gasto.html', {'form': form})
    
@login_required
def historial_movimientos_view(request):
    query = request.GET.get('q', '')
    
    movimientos = Movimiento.objects.filter(cuenta__usuario=request.user)

    if query:
        movimientos = movimientos.filter(
            Q(descripcion__icontains=query) |
            Q(categoria__nombre_categoria__icontains=query) |
            Q(cuenta__nombre_cuenta__icontains=query)
        )

    movimientos = movimientos.order_by('-fecha_creacion')

    contexto = {
        'movimientos': movimientos,
        'query': query, 
    }
    
    return render(request, 'movimientos.html', contexto)

@login_required
def editar_movimiento_view(request, mov_id):
    movimiento = get_object_or_404(Movimiento, id=mov_id, cuenta__usuario=request.user)
    
    if request.method == 'POST':
        with transaction.atomic():
            cuenta = movimiento.cuenta
            viejo_monto = movimiento.cantidad_moneda
            nuevo_monto = decimal(request.POST.get('cantidad_moneda', viejo_monto))
            
            if nuevo_monto <= 0:
                messages.error(request, "El monto debe ser mayor a cero.")
                return redirect('historial_movimientos')

            diferencia = nuevo_monto - viejo_monto
            
            es_ingreso = movimiento.tipo_movimiento.nombre_movimiento == 'Ingreso' or (movimiento.tipo_movimiento.nombre_movimiento == 'transferencia' and 'Recibido de' in movimiento.descripcion)
            
            if es_ingreso:
                cuenta.saldo_inicial_cuenta += diferencia
            else:
                cuenta.saldo_inicial_cuenta -= diferencia
                
            cuenta.save()
            
            movimiento.cantidad_moneda = nuevo_monto
            movimiento.descripcion = request.POST.get('descripcion', movimiento.descripcion)
            movimiento.save()
            
            messages.success(request, "El movimiento ha sido actualizado.")
            
    return redirect('historial_movimientos')

@login_required
def eliminar_movimiento_view(request, mov_id):
    movimiento = get_object_or_404(Movimiento, id=mov_id, cuenta__usuario=request.user)
    
    if request.method == 'POST':
        with transaction.atomic():
            cuenta = movimiento.cuenta
            monto = movimiento.cantidad_moneda
            es_ingreso = movimiento.tipo_movimiento.nombre_movimiento == 'Ingreso' or (movimiento.tipo_movimiento.nombre_movimiento == 'transferencia' and 'Recibido de' in movimiento.descripcion)
            
            if es_ingreso:
                cuenta.saldo_inicial_cuenta -= monto
            else:
                cuenta.saldo_inicial_cuenta += monto
                
            cuenta.save()
            movimiento.delete()
            
            messages.success(request, "Movimiento eliminado. El saldo de tu cuenta fue restaurado.")
            
    return redirect('historial_movimientos')

@login_required
def transferencia_view(request):
    tipo_transferencia, created = TipoMovimiento.objects.get_or_create(nombre_movimiento="transferencia")
    categoria_transferencia, created = Categoria.objects.get_or_create(nombre_categoria="Transferencia", defaults={'tipo_categoria': 'transferencia'})

    if request.method == 'POST':
        form = TransferenciaForm(request.POST, user=request.user)

        if form.is_valid():
            movimiento_base = form.save(commit=False)
            cuenta_origen = movimiento_base.cuenta
            cuenta_destino = form.cleaned_data['cuenta_destino']
            cantidad = movimiento_base.cantidad_moneda
            descripcion_original = movimiento_base.descripcion or ""

            if cuenta_origen.saldo_inicial_cuenta < cantidad:
                messages.error(request, f"Saldo insuficiente. La cuenta {cuenta_origen.nombre_cuenta} solo tiene {cuenta_origen.saldo_inicial_cuenta}.")
                return render(request, 'transferencia.html', {'form': form})

            with transaction.atomic():
                Movimiento.objects.create(
                    cuenta=cuenta_origen,
                    categoria=categoria_transferencia,
                    tipo_movimiento=tipo_transferencia,
                    cantidad_moneda=cantidad,
                    fecha_creacion=movimiento_base.fecha_creacion,
                    descripcion=f"Enviado a {cuenta_destino.nombre_cuenta}. {descripcion_original}",
                    moneda=cuenta_origen.moneda,
                )
                cuenta_origen.saldo_inicial_cuenta -= cantidad
                cuenta_origen.save()

                Movimiento.objects.create(
                    cuenta=cuenta_destino,
                    categoria=categoria_transferencia,
                    tipo_movimiento=tipo_transferencia,
                    cantidad_moneda=cantidad,
                    fecha_creacion=movimiento_base.fecha_creacion,
                    descripcion=f"Recibido de {cuenta_origen.nombre_cuenta}. {descripcion_original}",
                    moneda=cuenta_destino.moneda,
                )
                cuenta_destino.saldo_inicial_cuenta += cantidad
                cuenta_destino.save()

            return redirect('dashboard')
    else:
        form = TransferenciaForm(user=request.user)

    return render(request, 'transferencia.html', {'form': form})

@login_required
# Asegúrate de importar el nuevo formulario en la parte superior:
# from .forms import ..., CambiarPreguntaSeguridadForm

@login_required
def perfil_view(request):
    usuario = request.user
    
    form_perfil = EditarPerfilForm(instance=usuario)
    form_password = CustomPasswordChangeForm(user=usuario)
    # NUEVO: Instanciamos el formulario de la pregunta de seguridad
    form_pregunta = CambiarPreguntaSeguridadForm(instance=usuario)
    
    if request.method == 'POST':
        if 'btn_guardar_perfil' in request.POST:
            form_perfil = EditarPerfilForm(request.POST, instance=usuario)
            if form_perfil.is_valid():
                form_perfil.save()
                messages.success(request, "Tus datos personales han sido actualizados.")
                return redirect('perfil') 
                
        elif 'btn_cambiar_password' in request.POST:
            form_password = CustomPasswordChangeForm(user=usuario, data=request.POST)
            if form_password.is_valid():
                form_password.save()
                update_session_auth_hash(request, form_password.user) 
                messages.success(request, "Tu contraseña ha sido modificada con éxito.")
                return redirect('perfil')

        # NUEVO: Procesamos el guardado de la pregunta de seguridad
        elif 'btn_cambiar_pregunta' in request.POST:
            form_pregunta = CambiarPreguntaSeguridadForm(request.POST, instance=usuario)
            if form_pregunta.is_valid():
                form_pregunta.save()
                messages.success(request, "Tu pregunta de seguridad ha sido actualizada correctamente.")
                return redirect('perfil')

    contexto = {
        'form_perfil': form_perfil,
        'form_password': form_password,
        'form_pregunta': form_pregunta,
    }
    
    return render(request, 'perfil.html', contexto)


@login_required
def salir_view(request):
    logout(request)
    return redirect('login')


    correo = request.session.get('correo_recuperacion')
    verificado = request.session.get('codigo_verificado')
    
    if not correo or not verificado:
        return redirect('solicitar_codigo')
        
    if request.method == 'POST':
        form = RestablecerPasswordForm(request.POST)
        if form.is_valid():
            usuario = Usuario.objects.get(correo_usuario=correo)
            
            # Cambiar y encriptar contraseña
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()
            
            # Invalidar todos los códigos anteriores de este usuario
            CodigoRecuperacion.objects.filter(usuario=usuario, usado=False).update(usado=True)
            
            # Limpiar variables de sesión
            del request.session['correo_recuperacion']
            del request.session['codigo_verificado']
            
            messages.success(request, "Tu contraseña ha sido restablecida con éxito. Ya puedes iniciar sesión.")
            return redirect('login')
    else:
        form = RestablecerPasswordForm()
    return render(request, 'registration/restablecer_password.html', {'form': form})

def recuperar_correo_view(request):
    if request.method == 'POST':
        form = RecuperarCorreoForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            try:
                usuario = Usuario.objects.get(correo_usuario=correo)
                # Guardamos el correo en sesión de forma segura
                request.session['recuperacion_correo'] = correo
                return redirect('recuperar_pregunta')
            except Usuario.DoesNotExist:
                form.add_error('correo', "Este correo no está registrado en el sistema.")
    else:
        form = RecuperarCorreoForm()
    return render(request, 'registration/recuperar_correo.html', {'form': form})

def recuperar_pregunta_view(request):
    correo = request.session.get('recuperacion_correo')
    if not correo:
        return redirect('recuperar_correo')
        
    usuario = Usuario.objects.get(correo_usuario=correo)
    pregunta_texto = dict(Usuario.PREGUNTAS_CHOICES).get(usuario.pregunta_seguridad)

    if request.method == 'POST':
        form = RecuperarRespuestaForm(request.POST)
        if form.is_valid():
            respuesta_ingresada = form.cleaned_data['respuesta']
            
            # Verificamos si la respuesta coincide (ambas están en minúsculas)
            if respuesta_ingresada == usuario.respuesta_seguridad:
                request.session['recuperacion_aprobada'] = True
                return redirect('recuperar_nueva_clave')
            else:
                form.add_error('respuesta', "Respuesta incorrecta. Inténtalo de nuevo.")
    else:
        form = RecuperarRespuestaForm()
        
    return render(request, 'registration/recuperar_pregunta.html', {
        'form': form, 
        'pregunta_texto': pregunta_texto
    })

def recuperar_nueva_clave_view(request):
    correo = request.session.get('recuperacion_correo')
    aprobada = request.session.get('recuperacion_aprobada')
    
    if not correo or not aprobada:
        return redirect('recuperar_correo')
        
    if request.method == 'POST':
        form = RestablecerPasswordForm(request.POST) # Utilizamos el form de restablecer que ya tenías
        if form.is_valid():
            usuario = Usuario.objects.get(correo_usuario=correo)
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()
            
            # Limpiar sesión
            del request.session['recuperacion_correo']
            del request.session['recuperacion_aprobada']
            
            messages.success(request, "Tu contraseña ha sido restablecida. Inicia sesión con tu nueva clave.")
            return redirect('login')
    else:
        form = RestablecerPasswordForm()
        
    return render(request, 'registration/restablecer_password.html', {'form': form})