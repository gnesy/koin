# Koin

## Descripción del Proyecto

Koin es un sistema de información y gestión financiera desarrollado como Trabajo Especial de Grado para la Comunidad del Sector Andrés Eloy Blanco 3 del Municipio Carirubana, Estado Falcón, Venezuela. 

### ¿Qué es Koin?
Koin es una aplicación web orientada a la gestión económica y simulación financiera, que integra capacidades de Aplicación Web Progresiva (PWA). Está estructurada para registrar, monitorear y proyectar datos, ofreciendo una interfaz accesible e intuitiva para los usuarios del sector.

### ¿Para qué sirve?
El sistema permite a los usuarios llevar un control riguroso de sus finanzas personales, comerciales o comunitarias. A través de sus módulos internos de finanzas y simulación, facilita el registro detallado de transacciones, la visualización de balances generales y la consulta de tasas de cambio monetario actualizadas, gracias a su integración con los indicadores oficiales del Banco Central de Venezuela (BCV).

### ¿Qué soluciona?
La herramienta aborda la necesidad directa de la comunidad del Sector Andrés Eloy Blanco 3 de contar con un mecanismo automatizado, confiable y adaptado a la realidad económica venezolana para administrar sus recursos. El sistema erradica la dependencia de registros manuales informales, minimiza los errores de cálculo en conversiones multimoneda y provee una plataforma tecnológica unificada para optimizar la planificación financiera y la toma de decisiones económicas.

## Stack Tecnológico

El proyecto ha sido construido utilizando un conjunto de tecnologías modernas y eficientes para garantizar su estabilidad y escalabilidad:

*   **Lenguaje de Programación:** Python 3.12
*   **Framework Backend:** Django 6.0.5
*   **Frontend:** HTML, CSS, JavaScript (Django Templates)
*   **Progresive Web App (PWA):** Implementación a través de `django-pwa` y Service Workers.
*   **Integraciones y Web Scraping:** `pyBCV` (para obtención de datos del BCV), `BeautifulSoup4` y `requests`.
*   **Infraestructura y Despliegue:** Docker y Docker Compose.

## Ejecución Local del Proyecto

El sistema ha sido configurado para poder ejecutarse en entornos locales de dos maneras: utilizando un entorno virtual de Python convencional o mediante contenedores de Docker para garantizar el aislamiento del sistema.

### Ejecución sin Docker

Para ejecutar el proyecto directamente sobre su sistema operativo base, siga las siguientes instrucciones:

1.  **Clonar el repositorio y acceder al directorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd koin
    ```

2.  **Crear y activar un entorno virtual:**
    *   En sistemas basados en Linux/macOS:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   En sistemas basados en Windows:
        ```cmd
        python -m venv venv
        venv\Scripts\activate
        ```

3.  **Instalar las dependencias requeridas:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Aplicar las migraciones de la base de datos:**
    ```bash
    python manage.py migrate
    ```

5.  **Iniciar el servidor de desarrollo:**
    ```bash
    python manage.py runserver
    ```

6.  **Acceder a la plataforma:**
    Abra su navegador web de preferencia e ingrese a la dirección `http://localhost:8000`.

### Ejecución con Docker

Para una implementación estandarizada que prevenga problemas de compatibilidad entre dependencias, se recomienda utilizar Docker.

1.  **Requisitos previos:** 
    Verifique que los servicios de Docker y Docker Compose se encuentren instalados y en ejecución en su sistema.

2.  **Clonar el repositorio y acceder al directorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd koin
    ```

3.  **Construir e iniciar los contenedores:**
    ```bash
    docker-compose up --build
    ```
    *Nota: Para ejecutar los contenedores en segundo plano, agregue el parámetro `-d` (`docker-compose up -d --build`).*

4.  **Aplicar las migraciones iniciales:**
    Con los contenedores en ejecución, abra otra terminal y ejecute:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

5.  **Acceder a la plataforma:**
    Abra su navegador web de preferencia e ingrese a la dirección `http://localhost:8000`.
