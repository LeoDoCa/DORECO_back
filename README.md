# DORECO_back

## Integrantes del Equipo
- Andrés Yismael Díaz Hernández
- Leonardo Daniel Dorantes Castañeda
- Brandon Alfredo Hernández Rodríguez
- Vulmaro Alberto Martínez Verdugo
- Martin Ortega Montes
- Anett Yomali Vera Carbajal

## Descripción del Sistema
El proyecto DORECO (Donación y Reciclaje en la Comunidad Universitaria) es un sistema orientado a promover la cultura del reciclaje, consumo responsable, reutilización y apoyo colaborativo dentro de la comunidad universitaria.  
El sistema permite a los estudiantes publicar objetos que ya no utilizan, tales como ropa, libros o útiles escolares, con la finalidad de donarlos, venderlos o prestarlos con otros compañeros.  
Entre sus principales funcionalidades se encuentran:  
- Registro de objetos con fotografías, descripciones, estado, categoría.
- Búsqueda y filtrado de objetos disponibles.
- Generación de códigos QR para acceso rápido a la información de cada artículo.
- Módulo de administración para la gestión de categorías, control de publicaciones y reportes sobre el destino de los objetos (donados, vendidos, prestados).

Esta es la parte backend del proyecto, desarrollada en Python utilizando el framework Django, encargada de manejar la lógica del sistema, interacción con la base de datos y administración de recursos.  

## Estructura de Carpetas
```bash
DORECO_back/
├── assets/
|   └── test_assets.txt
├── data/
|   └── test_data.txt
├── docs/
|   └── test_docs.txt 
├── src/
│   ├── DORECO_back/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py     
│   │   ├── urls.py       
│   │   └── wsgi.py
│   ├── .gitignore         
│   └── manage.py
├── tests/
|   └── test_tests.txt             
└── README.md             
```

## Requisitos Previos
- Python 3.x
- Django
- Servicio de MySQL

## Cómo Clonar y Correr el Proyecto
```bash
# 1. Clonar el repositorio
git clone https://github.com/LeoDoCa/DORECO_back.git

# 2. Acceder a la carpeta del proyecto
cd .\src\
cd .\DORECO_back\

# 3. Crear la base de datos doreco_db (si es necesario)
# Revisar la configuración de la base de datos en:
# \src\DORECO_back\DORECO_back\settings.py

# 4. Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# 5. Ejecutar el servidor de desarrollo
python manage.py runserver
```

## Notas Adicionales
- Revisa y ajusta las credenciales de la base de datos en /src/DORECO_back/DORECO_back/settings.py si es necesario.
- Este proyecto no incluye todavía una interfaz frontend; esta se desarrollará o integrará en un repositorio separado llamado DORECO_front.
