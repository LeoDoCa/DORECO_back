# Documentación de Endpoints API - DORECO

Esta documentación describe todos los endpoints disponibles en la API de DORECO para realizar operaciones CRUD y funcionalidades específicas.

## Base URL
```
http://localhost:8000
```

## Autenticación
La API utiliza JWT (JSON Web Tokens) para autenticación. Debes incluir el token en el header:
```
Authorization: Bearer <tu_access_token>
```

## Endpoints de Autenticación

### 1. Registro de Usuario
**POST** `/auth/register/`
```json
{
    "name": "Juan",
    "surnames": "Pérez García",
    "email": "juan@example.com",
    "username": "juanperez",
    "password": "password123",
    "password_confirm": "password123",
    "phone_number": "+525551234567"
}
```

### 2. Login
**POST** `/auth/login/`
```json
{
    "email": "juan@example.com",
    "password": "password123"
}
```

### 3. Logout
**POST** `/auth/logout/`
```json
{
    "refresh": "<refresh_token>"
}
```

### 4. Obtener Perfil
**GET** `/auth/profile/`
Headers: `Authorization: Bearer <access_token>`

### 5. Actualizar Perfil
**PUT/PATCH** `/auth/update-profile/`
```json
{
    "name": "Juan Carlos",
    "phone_number": "+525551234568"
}
```

### 6. Cambiar Contraseña
**POST** `/auth/change-password/`
```json
{
    "old_password": "password123",
    "new_password": "newpassword123",
    "new_password_confirm": "newpassword123"
}
```

## Endpoints de Usuarios

### 1. Listar Usuarios (Solo Admins)
**GET** `/api/users/`
Headers: `Authorization: Bearer <access_token>`

### 2. Crear Usuario
**POST** `/api/users/`
```json
{
    "name": "María",
    "surnames": "González López",
    "email": "maria@example.com",
    "username": "mariagonzalez",
    "password": "password123",
    "password_confirm": "password123"
}
```

### 3. Obtener Usuario por ID
**GET** `/api/users/{id}/`

### 4. Actualizar Usuario
**PUT/PATCH** `/api/users/{id}/`

### 5. Eliminar Usuario
**DELETE** `/api/users/{id}/`

### 6. Buscar Usuarios (Solo Admins)
**GET** `/auth/search/?q=juan`

## Endpoints de Roles

### 1. Listar Roles
**GET** `/api/roles/`

### 2. Crear Rol (Solo Admins)
**POST** `/api/roles/`
```json
{
    "name": "Moderador"
}
```

### 3. Obtener Rol por ID
**GET** `/api/roles/{id}/`

### 4. Actualizar Rol (Solo Admins)
**PUT/PATCH** `/api/roles/{id}/`

### 5. Eliminar Rol (Solo Admins)
**DELETE** `/api/roles/{id}/`

## Endpoints de Categorías

### 1. Listar Categorías
**GET** `/api/categories/`
Query params: `?search=libros&is_active=true`

### 2. Crear Categoría
**POST** `/api/categories/`
```json
{
    "name": "Libros",
    "description": "Libros de todos los géneros"
}
```
**Nota**: Los usuarios normales pueden sugerir categorías (se crean como inactivas). Solo admins pueden crear categorías activas directamente.

### 3. Obtener Categoría por ID
**GET** `/api/categories/{id}/`

### 4. Actualizar Categoría (Solo Admins)
**PUT/PATCH** `/api/categories/{id}/`

### 5. Eliminar Categoría (Solo Admins)
**DELETE** `/api/categories/{id}/`

### 6. Obtener Solo Categorías Activas
**GET** `/api/categories/active/`

### 7. Obtener Categorías Sugeridas (Solo Admins)
**GET** `/api/categories/suggested/`

### 8. Activar/Desactivar Categoría (Solo Admins)
**POST** `/api/categories/{id}/toggle-status/`

## Endpoints de Publicaciones

### 1. Listar Publicaciones
**GET** `/api/publications/`
Query params: `?search=libro&category=1&type=donation&condition=good&status=available`

### 2. Crear Publicación
**POST** `/api/publications/`
```json
{
    "title": "Silla rústica",
    "description": "Silla hecha de madera reciclada",
    "category": 1,
    "condition": "good",
    "publication_type": "sale",
    "price": "250.00",
    "keywords": "madera, rústico, reciclaje",
    "duration": "P1D",
    "status": "available",
    "is_active": true
}
```
**Nota**: El campo `owner` se asigna automáticamente al usuario autenticado.

### 3. Obtener Publicación por ID
**GET** `/api/publications/{uuid}/`

### 4. Actualizar Publicación
**PUT/PATCH** `/api/publications/{uuid}/`

### 5. Eliminar Publicación
**DELETE** `/api/publications/{uuid}/`

### 6. Mis Publicaciones
**GET** `/api/publications/my-publications/`

### 7. Agregar/Quitar Favorito
**POST** `/api/publications/{uuid}/toggle-favorite/`

### 8. Cambiar Estado de Publicación
**PATCH** `/api/publications/{uuid}/change-status/`
```json
{
    "status": "completed"
}
```

## Endpoints de Favoritos

### 1. Listar Mis Favoritos
**GET** `/api/favorites/`

### 2. Agregar a Favoritos
**POST** `/api/favorites/add/`
```json
{
    "publication": "uuid-de-publicacion"
}
```

### 3. Eliminar de Favoritos
**DELETE** `/api/favorites/remove/`
```json
{
    "publication": "uuid-de-publicacion"
}
```

### 4. Eliminar Favorito por ID
**DELETE** `/api/favorites/{id}/`

## Endpoints de Reportes

### 1. Listar Reportes
**GET** `/api/reports/`
Query params: `?status=pending&reason=spam`

### 2. Crear Reporte
**POST** `/api/reports/`
```json
{
    "publication": "uuid-de-publicacion",
    "reason": "inappropriate",
    "description": "Contenido inapropiado en la descripción"
}
```

### 3. Obtener Reporte por ID
**GET** `/api/reports/{id}/`

### 4. Mis Reportes
**GET** `/api/reports/my-reports/`

### 5. Reportes Pendientes (Solo Admins)
**GET** `/api/reports/pending/`

### 6. Resolver Reporte (Solo Admins)
**PATCH** `/api/reports/{id}/resolve/`
```json
{
    "status": "resolved",
    "admin_comment": "Problema resuelto, contenido removido"
}
```

### 7. Estadísticas de Reportes (Solo Admins)
**GET** `/api/reports/statistics/`

## Endpoints de Administración

### 1. Estadísticas del Sistema

#### Listar Estadísticas (Solo Admins)
**GET** `/api/system-stats/`
Query params: `?start_date=2024-01-01&end_date=2024-12-31`

#### Crear Estadísticas (Solo Admins)
**POST** `/api/system-stats/`
```json
{
    "date": "2024-01-15",
    "total_publications": 100,
    "total_donations": 50,
    "total_loans": 30,
    "total_sales": 20,
    "active_users": 200,
    "new_users": 5
}
```

#### Generar Estadísticas de Hoy (Solo Admins)
**POST** `/api/system-stats/generate-today/`

#### Estadísticas Recientes (Solo Admins)
**GET** `/api/system-stats/recent/?days=7`

### 2. Acciones Administrativas

#### Listar Acciones (Solo Admins)
**GET** `/api/admin-actions/`

#### Crear Acción (Solo Admins)
**POST** `/api/admin-actions/`
```json
{
    "action_type": "ban_user",
    "target_id": "123",
    "description": "Usuario baneado por comportamiento inapropiado"
}
```

#### Mis Acciones (Solo Admins)
**GET** `/api/admin-actions/my-actions/`

### 3. Dashboard

#### Estadísticas del Dashboard (Solo Admins)
**GET** `/api/dashboard/stats/`

#### Actividad Reciente (Solo Admins)
**GET** `/api/dashboard/recent-activity/`

#### Estado del Sistema (Solo Admins)
**GET** `/api/dashboard/system-health/`

## Códigos de Estado HTTP

- `200 OK` - Operación exitosa
- `201 Created` - Recurso creado exitosamente
- `400 Bad Request` - Datos inválidos
- `401 Unauthorized` - Token de autenticación requerido o inválido
- `403 Forbidden` - Sin permisos para realizar la acción
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error del servidor

## Ejemplos de Filtros y Búsquedas

### Publicaciones
```
GET /api/publications/?search=libro&category=1&type=donation&condition=good&status=available&owner=123
```

### Categorías
```
GET /api/categories/?search=tecnología&is_active=true
```

### Reportes
```
GET /api/reports/?status=pending&reason=spam&publication=uuid
```

### Usuarios (Solo Admins)
```
GET /auth/search/?q=juan
```

## Consideraciones Importantes

1. **Autenticación**: La mayoría de endpoints requieren autenticación JWT
2. **Permisos**: Algunos endpoints están restringidos a administradores
3. **Validaciones**: Todos los datos son validados antes de ser procesados
4. **UUIDs**: Las publicaciones usan UUIDs como identificadores
5. **Paginación**: Los listados largos pueden estar paginados
6. **CORS**: Configurado para desarrollo local

## Ejemplos de Uso Completo

### 1. Flujo de Registro y Publicación
1. `POST /api/users/` - Registrar usuario
2. `POST /auth/login/` - Hacer login
3. `GET /api/categories/active/` - Obtener categorías
4. `POST /api/publications/` - Crear publicación

### 2. Flujo de Reporte
1. `POST /auth/login/` - Login como usuario
2. `POST /api/reports/` - Crear reporte
3. `POST /auth/login/` - Login como admin
4. `GET /api/reports/pending/` - Ver reportes pendientes
5. `PATCH /api/reports/{id}/resolve/` - Resolver reporte 