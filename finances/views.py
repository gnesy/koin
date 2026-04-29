from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import TemplateView # <- Aquí importamos la herramienta para el Dashboard

# 1. La vista de tu pantalla principal
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

# 2. La vista de tu pantalla de registro
def registro_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('dashboard') 
    else:
        form = UserCreationForm()
        
    return render(request, 'registration/signup.html', {'form': form})