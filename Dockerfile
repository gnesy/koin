# 1. Base oficial de Python ligera
FROM python:3.12-slim

# 2. Configurar variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Carpeta de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalar las dependencias de tu proyecto
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar todo el código fuente al contenedor
COPY . /app/

# 6. Exponer el puerto predeterminado
EXPOSE 8000

# 7. Comando para arrancar el servidor de desarrollo
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]