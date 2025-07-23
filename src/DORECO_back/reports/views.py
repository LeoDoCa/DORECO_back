from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Report
from .serializers import (
    ReportSerializer, CreateReportSerializer, AdminReportSerializer,
    ReportListSerializer
)


class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar reportes"""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar reportes según el usuario"""
        if self.request.user.is_staff or self.request.user.is_admin:
            # Admins ven todos los reportes
            queryset = Report.objects.select_related(
                'publication', 'reported_by', 'reviewed_by'
            ).order_by('-created_at')
        else:
            # Usuarios normales solo ven sus reportes
            queryset = Report.objects.filter(reported_by=self.request.user).select_related(
                'publication', 'reviewed_by'
            ).order_by('-created_at')
        
        # Filtros
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        reason_filter = self.request.query_params.get('reason', None)
        if reason_filter:
            queryset = queryset.filter(reason=reason_filter)
        
        # Filtro por publicación (solo para admins)
        publication_id = self.request.query_params.get('publication', None)
        if publication_id and (self.request.user.is_staff or self.request.user.is_admin):
            queryset = queryset.filter(publication_id=publication_id)
        
        return queryset
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción y usuario"""
        if self.action == 'create':
            return CreateReportSerializer
        elif self.action == 'list':
            return ReportListSerializer
        elif self.request.user.is_staff or self.request.user.is_admin:
            return AdminReportSerializer
        return ReportSerializer
    
    def get_permissions(self):
        """Permisos específicos por acción"""
        if self.action in ['update', 'partial_update', 'destroy']:
            # Solo admins pueden actualizar/eliminar reportes
            if not (self.request.user.is_staff or self.request.user.is_admin):
                self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
    def perform_update(self, serializer):
        """Solo admins pueden actualizar reportes"""
        if not (self.request.user.is_staff or self.request.user.is_admin):
            raise PermissionError("Solo los administradores pueden actualizar reportes.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Solo admins pueden eliminar reportes"""
        if not (self.request.user.is_staff or self.request.user.is_admin):
            raise PermissionError("Solo los administradores pueden eliminar reportes.")
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        """Obtener reportes del usuario autenticado"""
        reports = Report.objects.filter(reported_by=request.user).select_related(
            'publication', 'reviewed_by'
        ).order_by('-created_at')
        
        serializer = ReportListSerializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Obtener reportes pendientes (solo admins)"""
        if not (request.user.is_staff or request.user.is_admin):
            return Response({"error": "No tienes permisos para ver reportes pendientes"}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        pending_reports = Report.objects.filter(status='pending').select_related(
            'publication', 'reported_by'
        ).order_by('-created_at')
        
        serializer = AdminReportSerializer(pending_reports, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def resolve(self, request, pk=None):
        """Resolver un reporte (solo admins)"""
        if not (request.user.is_staff or request.user.is_admin):
            return Response({"error": "No tienes permisos para resolver reportes"}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        report = self.get_object()
        new_status = request.data.get('status')
        admin_comment = request.data.get('admin_comment', '')
        
        if new_status not in ['reviewed', 'resolved', 'dismissed']:
            return Response({"error": "Estado inválido"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        report.status = new_status
        report.admin_comment = admin_comment
        report.reviewed_by = request.user
        report.save()
        
        serializer = AdminReportSerializer(report, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Obtener estadísticas de reportes (solo admins)"""
        if not (request.user.is_staff or request.user.is_admin):
            return Response({"error": "No tienes permisos para ver estadísticas"}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        stats = {
            'total_reports': Report.objects.count(),
            'pending_reports': Report.objects.filter(status='pending').count(),
            'reviewed_reports': Report.objects.filter(status='reviewed').count(),
            'resolved_reports': Report.objects.filter(status='resolved').count(),
            'dismissed_reports': Report.objects.filter(status='dismissed').count(),
            'reports_by_reason': {}
        }
        
        # Estadísticas por razón
        for choice in Report.REASON_CHOICES:
            reason_code = choice[0]
            reason_name = choice[1]
            count = Report.objects.filter(reason=reason_code).count()
            stats['reports_by_reason'][reason_name] = count
        
        return Response(stats)
