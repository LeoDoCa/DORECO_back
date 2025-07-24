from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet

# Crear router para las APIs REST
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')

urlpatterns = [
    # URLs del router (incluye todas las acciones CRUD automáticamente)
    path('api/', include(router.urls)),
    
    # URLs adicionales
    path('api/categories/active/', CategoryViewSet.as_view({'get': 'active'}), name='categories-active'),
    path('api/categories/suggested/', CategoryViewSet.as_view({'get': 'suggested'}), name='categories-suggested'),
    path('api/categories/<int:pk>/toggle-status/', CategoryViewSet.as_view({'post': 'toggle_status'}), name='categories-toggle-status'),
]
