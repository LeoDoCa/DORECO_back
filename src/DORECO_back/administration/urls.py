from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SystemStatsViewSet, AdminActionViewSet, DashboardViewSet

# Crear router para las APIs REST
router = DefaultRouter()
router.register(r'system-stats', SystemStatsViewSet, basename='system-stats')
router.register(r'admin-actions', AdminActionViewSet, basename='admin-actions')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    # URLs del router (incluye todas las acciones CRUD automáticamente)
    path('api/', include(router.urls)),
    
    # URLs adicionales para estadísticas del sistema
    path('api/system-stats/generate-today/', SystemStatsViewSet.as_view({'post': 'generate_today_stats'}), name='system-stats-generate-today'),
    path('api/system-stats/recent/', SystemStatsViewSet.as_view({'get': 'recent_stats'}), name='system-stats-recent'),
    
    # URLs adicionales para acciones administrativas
    path('api/admin-actions/my-actions/', AdminActionViewSet.as_view({'get': 'my_actions'}), name='admin-actions-my-actions'),
    
    # URLs adicionales para dashboard
    path('api/dashboard/stats/', DashboardViewSet.as_view({'get': 'stats'}), name='dashboard-stats'),
    path('api/dashboard/recent-activity/', DashboardViewSet.as_view({'get': 'recent_activity'}), name='dashboard-recent-activity'),
    path('api/dashboard/system-health/', DashboardViewSet.as_view({'get': 'system_health'}), name='dashboard-system-health'),
]
