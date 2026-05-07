from pyBCV import Currency
from .models import Moneda

def obtener_tasa_bcv_segura():
    try:
        bcv = Currency()
        # Obtiene directamente la tasa del dólar como un float
        tasa_dolar = float(bcv.get_rate(currency_code='USD'))
        return tasa_dolar
    except Exception as e:
        print(f"Error con la librería pyBCV: {e}")
        return None


def actualizar_moneda_sistema():
    # Llama a la función que hayas elegido (manual o segura)
    nueva_tasa = obtener_tasa_bcv_segura() 
    
    if nueva_tasa:
        # Buscamos la moneda USD en tu base de datos o la creamos si no existe
        moneda_usd, created = Moneda.objects.get_or_create(
            codigo='USD',
            defaults={'nombre_moneda': 'Dólar Estadounidense', 'tasa_cambio': nueva_tasa}
        )
        
        # Si ya existía, actualizamos el valor
        if not created:
            moneda_usd.tasa_cambio = nueva_tasa
            moneda_usd.save()
            
        print(f"Éxito: Tasa actualizada a {nueva_tasa} Bs.")
        return True
    return False