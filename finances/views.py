from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import RegistroUsuarioForm
from django.contrib.auth.decorators import login_required
from .forms import LoginForm


@login_required
def dashboard(request):
    usuario = request.user

    contexto = {
        'familia' : usuario.nombre_familia_usuario,
        'nombre_completo' : f"{usuario.nombre_usuario} {usuario.apellido_usuario}"
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