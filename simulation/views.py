from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from finances.services import obtener_tasa_bcv_segura
import math

@login_required
def simulacion_view(request):
    # 1. ESTADO INICIAL
    ingreso_simulado = 0.00
    m_solicitado = ''
    meses = '' 
    
    ingreso_proyectado_usd = ingreso_proyectado_ves = 0.00
    gastos_totales_usd = gastos_totales_ves = 0.00
    
    necesidades_usd = deseos_usd = ahorro_usd = 0.00
    necesidades_ves = deseos_ves = ahorro_ves = 0.00
    
    costo_articulo = ''
    costo_articulo_float = 0.00
    fondo = 'necesidades'
    es_viable = True
    remanente_articulo = 0.00
    error_msg = None
    gasto_activo = 'false'
    
    # --- NUEVAS VARIABLES DE TIEMPO ACCIONABLE ---
    meses_necesarios = 0
    nombre_fondo = ''
    falta_dinero = 0.00
    fondo_evaluado = 0.00

    # Tasa BCV referencial
    tasa_bcv = obtener_tasa_bcv_segura()

    # 2. PROCESAMIENTO
    if 'monto' in request.GET and 'meses' in request.GET: 
        m_solicitado = request.GET.get('monto')
        meses_str = request.GET.get('meses')
        gasto_activo = request.GET.get('gasto_activo', 'false')
        
        if m_solicitado and meses_str:
            try:
                ingreso_simulado = float(m_solicitado)
                meses_int = int(meses_str)
                meses = str(meses_int) 
                
                if ingreso_simulado <= 0:
                    error_msg = "El ingreso mensual debe ser un número mayor a cero."
                    ingreso_simulado = 0.00 
                elif meses_int < 1 or meses_int > 24:
                    error_msg = "El plazo a proyectar debe estar entre 1 y 24 meses."
                    ingreso_simulado = 0.00 
                else:
                    costo_articulo = request.GET.get('costo_articulo', '').strip()
                    
                    if gasto_activo == 'true' and not costo_articulo:
                        error_msg = "Debe ingresar el costo del artículo si desea simular un gasto."
                        ingreso_simulado = 0.00
                    else:
                        # Cálculos base de la regla
                        ingreso_proyectado = ingreso_simulado * meses_int
                        
                        ingreso_proyectado_usd = round(ingreso_proyectado, 2)
                        ingreso_proyectado_ves = round(ingreso_proyectado_usd * tasa_bcv, 2)
                        
                        gastos_totales_usd = round(ingreso_proyectado_usd * 0.80, 2)
                        gastos_totales_ves = round(gastos_totales_usd * tasa_bcv, 2)
                        
                        necesidades_usd = round(ingreso_proyectado * 0.50, 2)
                        deseos_usd = round(ingreso_proyectado * 0.30, 2)
                        ahorro_usd = round(ingreso_proyectado * 0.20, 2)
                        
                        necesidades_ves = round(necesidades_usd * tasa_bcv, 2)
                        deseos_ves = round(deseos_usd * tasa_bcv, 2)
                        ahorro_ves = round(ahorro_usd * tasa_bcv, 2)
                        
                        if costo_articulo:
                            costo_articulo_float = float(costo_articulo)
                            
                            if costo_articulo_float < 0:
                                error_msg = "El costo del artículo no puede ser negativo."
                                ingreso_simulado = 0.00
                            else:
                                fondo = request.GET.get('fondo_afectado', 'necesidades')
                                
                                # Evaluamos asignación mensual y nombre del fondo según el radio seleccionado
                                if fondo == 'necesidades':
                                    fondo_evaluado = necesidades_usd
                                    asignacion_mensual = ingreso_simulado * 0.50
                                    nombre_fondo = "Necesidades Vitales (50%)"
                                elif fondo == 'deseos':
                                    fondo_evaluado = deseos_usd
                                    asignacion_mensual = ingreso_simulado * 0.30
                                    nombre_fondo = "Gastos Personales / Deseos (30%)"
                                else:
                                    fondo_evaluado = ahorro_usd
                                    asignacion_mensual = ingreso_simulado * 0.20
                                    nombre_fondo = "Reserva Patrimonial / Ahorro (20%)"
                                    
                                remanente_articulo = round(fondo_evaluado - costo_articulo_float, 2)
                                es_viable = remanente_articulo >= 0
                                
                                # CALCULO CRÍTICO: ¿Cuántos meses reales deben pasar?
                                if asignacion_mensual > 0:
                                    meses_necesarios = math.ceil(costo_articulo_float / asignacion_mensual)
                                else:
                                    meses_necesarios = 0
                                    
                                falta_dinero = round(costo_articulo_float - fondo_evaluado, 2)

            except ValueError:
                error_msg = "Por favor, introduzca valores numéricos válidos."
                meses = meses_str

    # 4. EMPAQUETADO Y ENVÍO AL TEMPLATE
    contexto = {
        'gasto_activo': gasto_activo,
        'ingreso_simulado': ingreso_simulado,
        'm_solicitado': m_solicitado,
        'meses': meses,
        'error_msg': error_msg,
        
        'ingreso_proyectado_usd': ingreso_proyectado_usd,
        'ingreso_proyectado_ves': ingreso_proyectado_ves,
        'gastos_totales_usd': gastos_totales_usd,
        'gastos_totales_ves': gastos_totales_ves,
        
        'tasa_bcv': tasa_bcv,
        'necesidades_usd': necesidades_usd, 'necesidades_ves': necesidades_ves,
        'deseos_usd': deseos_usd, 'deseos_ves': deseos_ves,
        'ahorro_usd': ahorro_usd, 'ahorro_ves': ahorro_ves,
        'costo_articulo': costo_articulo,
        'costo_articulo_float': costo_articulo_float,
        'fondo': fondo,
        'es_viable': es_viable,
        'remanente_articulo': remanente_articulo,
        
        # Nuevas variables enviadas
        'meses_necesarios': meses_necesarios,
        'nombre_fondo': nombre_fondo,
        'falta_dinero': falta_dinero,
        'fondo_evaluado': fondo_evaluado,
    }
    
    return render(request, 'simulacion.html', contexto)