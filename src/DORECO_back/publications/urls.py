from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PublicationViewSet, FavoriteViewSet

# Crear router para las APIs REST
router = DefaultRouter()
router.register(r'publications', PublicationViewSet, basename='publications')
router.register(r'favorites', FavoriteViewSet, basename='favorites')

urlpatterns = [
    # URLs del router (incluye todas las acciones CRUD automáticamente)
    path('api/', include(router.urls)),
    
    # URLs adicionales para publicaciones
    path('api/publications/my-publications/', PublicationViewSet.as_view({'get': 'my_publications'}), name='publications-my-publications'),
    path('api/publications/<uuid:pk>/toggle-favorite/', PublicationViewSet.as_view({'post': 'toggle_favorite'}), name='publications-toggle-favorite'),
    path('api/publications/<uuid:pk>/change-status/', PublicationViewSet.as_view({'patch': 'change_status'}), name='publications-change-status'),
    path('api/publications/<uuid:pk>/generate-qr/', PublicationViewSet.as_view({'get': 'generate_qr'}), name='publications-generate-qr'),
    
    # URLs adicionales para favoritos
    path('api/favorites/add/', FavoriteViewSet.as_view({'post': 'add_favorite'}), name='favorites-add'),
    path('api/favorites/remove/', FavoriteViewSet.as_view({'delete': 'remove_favorite'}), name='favorites-remove'),
]
