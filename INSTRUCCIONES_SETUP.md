# Instrucciones de Configuración y Prueba - DORECO Backend

## Configuración Inicial

### 1. Instalación de Dependencias
```bash
cd src/DORECO_back
pip install -r requirements.txt
```

### 2. Configuración de la Base de Datos

1. Crear archivo `conf.json` en `src/DORECO_back/DORECO_back/`:
```json
{
    "base_url": "http://localhost:8000",
    "secret_key": "tu_clave_secreta_aqui",
    "debug": true,
    "db": "doreco_db",
    "user": "root",
    "password": "tu_password_mysql",
    "server": "localhost",
    "puerto": "3306",
    "email_user": "tu-email@gmail.com",
    "email_password": "tu-password-de-aplicacion"
}
```

2. Crear la base de datos MySQL:
```sql
CREATE DATABASE doreco_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Migraciones y Configuración Inicial
```bash
# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Los usuarios se crean automáticamente con las migraciones
# No necesitas ejecutar comandos adicionales

# Crear superusuario manualmente (opcional)
python manage.py createsuperuser
```

### 4. Ejecutar el Servidor
```bash
python manage.py runserver
```

## Usuarios por Defecto Creados

### Administrador
- **Email**: admin@doreco.com
- **Password**: admin123456
- **Username**: admin
- **Rol**: ADMIN

### Usuario de Prueba
- **Email**: user@doreco.com
- **Password**: user123456
- **Username**: testuser
- **Rol**: USER

## Endpoints Principales para Pruebas con Postman

### Base URL
```
http://localhost:8000
```

## 1. Autenticación

### Login Admin
```
POST /auth/login/
Content-Type: application/json

{
    "email": "admin@doreco.com",
    "password": "admin123456"
}
```

### Login Usuario Normal
```
POST /auth/login/
Content-Type: application/json

{
    "email": "user@doreco.com",
    "password": "user123456"
}
```

### Registro de Nuevo Usuario
```
POST /auth/register/
Content-Type: application/json

{
    "name": "Juan",
    "surnames": "Pérez García",
    "email": "juan@ejemplo.com",
    "username": "juanperez",
    "password": "password123",
    "password_confirm": "password123",
    "phone_number": "+525551234567"
}
```

## 2. Categorías

### Listar Categorías (Público)
```
GET /api/categories/
```

### Sugerir Nueva Categoría (Usuario Autenticado)
```
POST /api/categories/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "Electrónicos",
    "description": "Dispositivos electrónicos y tecnología"
}
```

### Ver Categorías Sugeridas (Solo Admin)
```
GET /api/categories/suggested/
Authorization: Bearer <admin_access_token>
```

### Activar Categoría Sugerida (Solo Admin)
```
POST /api/categories/{id}/toggle-status/
Authorization: Bearer <admin_access_token>
```

## 3. Publicaciones

### Crear Publicación
```
POST /api/publications/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "Silla rústica",
    "description": "Silla hecha de madera reciclada",
    "category": 1,
    "condition": "good",
    "publication_type": "sale",
    "price": "250.00",
    "keywords": "madera, rústico, reciclaje"
}
```

### Listar Publicaciones (Público)
```
GET /api/publications/
```

### Filtrar Publicaciones
```
GET /api/publications/?search=silla&category=1&type=sale&condition=good&status=available
```

### Actualizar Publicación
```
PUT /api/publications/{uuid}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "Silla rústica vintage",
    "price": "280.00",
    "status": "reserved"
}
```

### Agregar/Quitar Favorito
```
POST /api/publications/{uuid}/toggle-favorite/
Authorization: Bearer <access_token>
```

### Mis Publicaciones
```
GET /api/publications/my-publications/
Authorization: Bearer <access_token>
```

## 4. Favoritos

### Listar Mis Favoritos
```
GET /api/favorites/
Authorization: Bearer <access_token>
```

### Agregar a Favoritos
```
POST /api/favorites/add/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "publication": "uuid-de-publicacion"
}
```

## 5. Reportes

### Crear Reporte
```
POST /api/reports/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "publication": "uuid-de-publicacion",
    "reason": "inappropriate",
    "description": "Contenido inapropiado en la descripción"
}
```

### Ver Reportes Pendientes (Solo Admin)
```
GET /api/reports/pending/
Authorization: Bearer <admin_access_token>
```

### Resolver Reporte (Solo Admin)
```
PATCH /api/reports/{id}/resolve/
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
    "status": "resolved",
    "admin_comment": "Problema resuelto, contenido removido"
}
```

## 6. Administración

### Dashboard Estadísticas (Solo Admin)
```
GET /api/dashboard/stats/
Authorization: Bearer <admin_access_token>
```

### Generar Estadísticas del Día (Solo Admin)
```
POST /api/system-stats/generate-today/
Authorization: Bearer <admin_access_token>
```

### Estado del Sistema (Solo Admin)
```
GET /api/dashboard/system-health/
Authorization: Bearer <admin_access_token>
```

## Flujos de Prueba Recomendados

### 1. Flujo Usuario Normal
1. Registrar usuario → `/auth/register/`
2. Login → `/auth/login/`
3. Ver categorías → `/api/categories/`
4. Sugerir nueva categoría → `POST /api/categories/`
5. Crear publicación → `POST /api/publications/`
6. Ver mis publicaciones → `/api/publications/my-publications/`
7. Agregar favorito → `POST /api/publications/{uuid}/toggle-favorite/`

### 2. Flujo Administrador
1. Login admin → `/auth/login/`
2. Ver categorías sugeridas → `/api/categories/suggested/`
3. Activar categoría → `POST /api/categories/{id}/toggle-status/`
4. Ver reportes pendientes → `/api/reports/pending/`
5. Resolver reporte → `PATCH /api/reports/{id}/resolve/`
6. Ver dashboard → `/api/dashboard/stats/`

## Consideraciones Importantes

1. **Tokens JWT**: Los tokens de acceso duran 1 hora, los de refresh 1 día
2. **Logout**: Incluye blacklist automático de tokens
3. **Permisos**: Los endpoints están protegidos según roles
4. **Validaciones**: Todos los datos son validados antes de ser procesados
5. **Categorías**: Los usuarios pueden sugerir, solo admins pueden activar
6. **Publicaciones**: Se pueden crear con categorías inactivas
7. **Favoritos**: Sistema completo de favoritos implementado

## Solución de Problemas Comunes

### Error de Conexión a Base de Datos
- Verificar que MySQL esté ejecutándose
- Confirmar credenciales en `conf.json`
- Asegurar que la base de datos existe

### Error 401 en Endpoints Protegidos
- Verificar que el token esté en el header
- Formato: `Authorization: Bearer <access_token>`
- El token puede haber expirado

### Error al Crear Categorías como Usuario
- Verificar que el usuario esté autenticado
- Las categorías se crean como sugerencias (inactivas)

### Error al Actualizar Publicaciones
- Solo el propietario o admin pueden actualizar
- Usar el endpoint específico de actualización 