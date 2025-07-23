from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet

# Crear router para las APIs REST
router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='reports')

urlpatterns = [
    # URLs del router (incluye todas las acciones CRUD automáticamente)
    path('api/', include(router.urls)),
    
    # URLs adicionales para reportes
    path('api/reports/my-reports/', ReportViewSet.as_view({'get': 'my_reports'}), name='reports-my-reports'),
    path('api/reports/pending/', ReportViewSet.as_view({'get': 'pending'}), name='reports-pending'),
    path('api/reports/<int:pk>/resolve/', ReportViewSet.as_view({'patch': 'resolve'}), name='reports-resolve'),
    path('api/reports/statistics/', ReportViewSet.as_view({'get': 'statistics'}), name='reports-statistics'),
]
