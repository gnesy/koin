from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .forms import RegistroUsuarioForm, LoginForm, CuentaForm
from .models import Cuenta


@login_required
def dashboard(request):
    usuario = request.user

    cuentas_del_usuario = Cuenta.objects.filter(usuario=usuario)

    suma_usd = cuentas_del_usuario.filter(moneda__codigo='USD').aggregate(total=Sum('saldo_inicial_cuenta'))['total']
    total_usd = suma_usd if suma_usd is not None else 0.00

    suma_ves = cuentas_del_usuario.filter(moneda__codigo='VES').aggregate(total=Sum('saldo_inicial_cuenta'))['total']
    total_ves = suma_ves if suma_ves is not None else 0.00

    contexto = {
        'cuentas': cuentas_del_usuario[:3],
        'total_cuentas': cuentas_del_usuario.count(),
        'familia' : usuario.nombre_familia_usuario,
        'nombre_completo' : f"{usuario.nombre_usuario} {usuario.apellido_usuario}",
        'total_usd': total_usd,
        'total_ves': total_ves,
    }

    return render(request, 'dashboard.html', contexto)
  

# La vista de tu pantalla de registro
def registro_usuario(request):
    if request.method == 'POST':
        # Le pasamos todos los datos que escribió el usuario al formulario
        form = RegistroUsuarioForm(request.POST)
        
        # is_valid() revisa automáticamente que los correos no se repitan y que todo esté correcto
        if form.is_valid():
            form.save()
            messages.success(request, "Se ha registrado correctamente")
            #login(request, nuevo_usuario)
            # return redirect('dashboard')
    else:
        # Si entra por primera vez, le mostramos el formulario vacío
        form = RegistroUsuarioForm()

    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    # Si el usuario ya inició sesión, no tiene sentido que vea el login, lo mandamos al dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        # AuthenticationForm requiere pasar el request como primer argumento
        form = LoginForm(request, data=request.POST)
        
        # is_valid() verifica si el correo existe y si la contraseña coincide
        if form.is_valid():
            # Extraemos el usuario autenticado y lo logueamos
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
    # Buscamos la cuenta, asegurándonos de que pertenezca al usuario actual
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, usuario=request.user)
    
    if request.method == 'POST':
        # Capturamos los datos enviados desde el HTML y los actualizamos
        cuenta.nombre_cuenta = request.POST.get('nombre_cuenta')
        cuenta.saldo_inicial_cuenta = request.POST.get('saldo_inicial_cuenta')
        cuenta.color_cuenta = request.POST.get('color_cuenta')
        cuenta.save()
        
    return redirect('cuentas')

@login_required
def eliminar_cuenta_view(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, usuario=request.user)
    
    if request.method == 'POST':
        cuenta.delete()
        
    return redirect('cuentas')
