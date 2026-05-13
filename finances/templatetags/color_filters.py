from django import template

# Registramos nuestra librería de filtros
register = template.Library()

@register.filter
def color_contraste(hex_color):
    """
    Toma un color hexadecimal y devuelve una clase de Tailwind
    ('text-white' o 'text-gray-900') para asegurar un buen contraste.
    """
    # Limpiamos el string por si viene con el símbolo '#' o está vacío
    if not hex_color:
        return 'text-gray-900'
        
    hex_color = hex_color.lstrip('#')
    
    # Manejamos hex de 3 caracteres (ej. 'FFF') expandiéndolo a 6 caracteres
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])

    try:
        # Convertimos los valores hexadecimales a enteros RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Fórmula YIQ para calcular el brillo (luminancia)
        yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
        
        # Si el valor YIQ es mayor a 128, el fondo es claro -> usamos texto oscuro.
        if yiq >= 128:
            return 'text-gray-900'
        else:
            return 'text-white'
            
    except ValueError:
        # En caso de que el código hex no sea válido, retornamos un color por defecto
        return 'text-gray-900'