from .services import obtener_tasa_bcv_segura

def datos_globales_koin(request):
    try:
        tasa_actual = obtener_tasa_bcv_segura() 
    except Exception as e:
        tasa_actual = "No disponible"

    return {
        'tasa_bcv_global': tasa_actual,
    }