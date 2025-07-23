from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, RoleViewSet

# Crear router para las APIs REST
router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'roles', RoleViewSet, basename='roles')

urlpatterns = [
    # URLs del router (incluye todas las acciones CRUD automáticamente)
    path('api/', include(router.urls)),
    
    # URLs adicionales para autenticación que no siguen el patrón REST estándar
    path('auth/login/', CustomUserViewSet.as_view({'post': 'login'}), name='user-login'),
    path('auth/logout/', CustomUserViewSet.as_view({'post': 'logout'}), name='user-logout'),
    path('auth/profile/', CustomUserViewSet.as_view({'get': 'profile'}), name='user-profile'),
    path('auth/update-profile/', CustomUserViewSet.as_view({'put': 'update_profile', 'patch': 'update_profile'}), name='user-update-profile'),
    path('auth/change-password/', CustomUserViewSet.as_view({'post': 'change_password'}), name='user-change-password'),
    path('auth/search/', CustomUserViewSet.as_view({'get': 'search'}), name='user-search'),
]
