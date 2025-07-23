from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta, date
from .models import SystemStats, AdminAction
from .serializers import (
    SystemStatsSerializer, AdminActionSerializer, AdminActionCreateSerializer,
    DashboardStatsSerializer, AdminActionListSerializer, SystemStatsCreateSerializer
)
from users.models import CustomUser
from publications.models import Publication
from reports.models import Report


class AdminRequiredMixin:
    """Mixin que requiere permisos de administrador"""
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_authenticated and 
                (request.user.is_staff or request.user.is_admin)):
            return Response({"error": "Se requieren permisos de administrador"}, 
                          status=status.HTTP_403_FORBIDDEN)
        return super().dispatch(request, *args, **kwargs)


class SystemStatsViewSet(AdminRequiredMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar estadísticas del sistema (solo admins)"""
    queryset = SystemStats.objects.all()
    serializer_class = SystemStatsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action == 'create':
            return SystemStatsCreateSerializer
        return SystemStatsSerializer
    
    def get_queryset(self):
        """Filtrar estadísticas por fecha si se especifica"""
        queryset = SystemStats.objects.all().order_by('-date')
        
        # Filtro por rango de fechas
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def generate_today_stats(self, request):
        """Generar estadísticas para el día actual"""
        today = date.today()
        
        # Verificar si ya existen estadísticas para hoy
        if SystemStats.objects.filter(date=today).exists():
            return Response({"error": "Ya existen estadísticas para hoy"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Calcular estadísticas
        stats_data = {
            'date': today,
            'total_publications': Publication.objects.count(),
            'total_donations': Publication.objects.filter(publication_type='donation').count(),
            'total_loans': Publication.objects.filter(publication_type='loan').count(),
            'total_sales': Publication.objects.filter(publication_type='sale').count(),
            'completed_donations': Publication.objects.filter(
                publication_type='donation', status='completed'
            ).count(),
            'completed_loans': Publication.objects.filter(
                publication_type='loan', status='completed'
            ).count(),
            'completed_sales': Publication.objects.filter(
                publication_type='sale', status='completed'
            ).count(),
            'active_users': CustomUser.objects.filter(is_active=True).count(),
            'new_users': CustomUser.objects.filter(created_at__date=today).count(),
        }
        
        stats = SystemStats.objects.create(**stats_data)
        serializer = SystemStatsSerializer(stats)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def recent_stats(self, request):
        """Obtener estadísticas de los últimos días"""
        days = int(request.query_params.get('days', 7))
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        stats = SystemStats.objects.filter(
            date__range=[start_date, end_date]
        ).order_by('-date')
        
        serializer = SystemStatsSerializer(stats, many=True)
        return Response(serializer.data)


class AdminActionViewSet(AdminRequiredMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar acciones administrativas (solo admins)"""
    queryset = AdminAction.objects.all()
    serializer_class = AdminActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action == 'create':
            return AdminActionCreateSerializer
        elif self.action == 'list':
            return AdminActionListSerializer
        return AdminActionSerializer
    
    def get_queryset(self):
        """Filtrar acciones por parámetros"""
        queryset = AdminAction.objects.select_related('admin_user').order_by('-created_at')
        
        # Filtro por tipo de acción
        action_type = self.request.query_params.get('action_type', None)
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        # Filtro por administrador
        admin_id = self.request.query_params.get('admin_id', None)
        if admin_id:
            queryset = queryset.filter(admin_user_id=admin_id)
        
        # Filtro por fecha
        start_date = self.request.query_params.get('start_date', None)
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_actions(self, request):
        """Obtener acciones del administrador autenticado"""
        actions = AdminAction.objects.filter(admin_user=request.user).order_by('-created_at')
        serializer = AdminActionListSerializer(actions, many=True)
        return Response(serializer.data)


class DashboardViewSet(AdminRequiredMixin, viewsets.ViewSet):
    """ViewSet para el dashboard administrativo"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Obtener estadísticas para el dashboard"""
        # Estadísticas generales
        total_users = CustomUser.objects.count()
        active_users = CustomUser.objects.filter(is_active=True).count()
        total_publications = Publication.objects.count()
        pending_reports = Report.objects.filter(status='pending').count()
        completed_transactions = Publication.objects.filter(status='completed').count()
        
        # Estadísticas recientes (últimos 7 días)
        recent_stats = SystemStats.objects.order_by('-date')[:7]
        
        dashboard_data = {
            'total_users': total_users,
            'active_users': active_users,
            'total_publications': total_publications,
            'pending_reports': pending_reports,
            'completed_transactions': completed_transactions,
            'recent_stats': recent_stats
        }
        
        serializer = DashboardStatsSerializer(dashboard_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Obtener actividad reciente del sistema"""
        # Últimas acciones administrativas
        recent_actions = AdminAction.objects.select_related('admin_user').order_by('-created_at')[:10]
        
        # Últimos reportes
        recent_reports = Report.objects.select_related(
            'reported_by', 'publication'
        ).order_by('-created_at')[:10]
        
        # Últimas publicaciones
        recent_publications = Publication.objects.select_related(
            'owner', 'category'
        ).order_by('-created_at')[:10]
        
        activity_data = {
            'recent_actions': AdminActionListSerializer(recent_actions, many=True).data,
            'recent_reports': Report.objects.filter(id__in=[r.id for r in recent_reports]).count(),
            'recent_publications': recent_publications.count(),
        }
        
        return Response(activity_data)
    
    @action(detail=False, methods=['get'])
    def system_health(self, request):
        """Verificar el estado del sistema"""
        health_data = {
            'total_users': CustomUser.objects.count(),
            'active_users': CustomUser.objects.filter(is_active=True).count(),
            'total_publications': Publication.objects.count(),
            'active_publications': Publication.objects.filter(is_active=True).count(),
            'pending_reports': Report.objects.filter(status='pending').count(),
            'resolved_reports': Report.objects.filter(status='resolved').count(),
            'system_status': 'healthy'  # Esto podría expandirse con más verificaciones
        }
        
        return Response(health_data)
