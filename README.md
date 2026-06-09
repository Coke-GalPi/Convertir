
# Convertir

Pequeña aplicación web en Flask para convertir entradas desde una interfaz pública y mostrar resultados.

## Resumen

Proyecto sencillo organizado con Flask. Incluye rutas públicas y plantillas para entrada y salida.

## Requisitos

- Python 3.8+ (recomendado)
- Dependencias en [requirements.txt](requirements.txt)

## Instalación (Windows)

1. Crear y activar un entorno virtual:

```
python -m venv venv
venv\Scripts\activate
```

2. Instalar dependencias:

```
pip install -r requirements.txt
```

## Ejecutar localmente

1. Ejecutar la aplicación directamente con Python:

```
python main.py
```

2. Alternativamente, usar `flask` si está configurado:

```
set FLASK_APP=main.py
flask run
```

La aplicación servirá páginas en `http://127.0.0.1:5000/` por defecto.


## Despliegue

Se incluye un `Procfile` para despliegue en plataformas compatibles con procesos tipo Heroku. Revisa y ajusta según el proveedor.

## Contribuir

1. Haz un fork del repositorio.
2. Crea una rama con tu cambio.
3. Envía un pull request describiendo la mejora.

## Contacto

Para preguntas o problemas, abre un issue en el repositorio o contacta al mantenedor.

