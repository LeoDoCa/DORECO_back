from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Category
from .serializers import CategorySerializer, CategoryListSerializer


# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar categorías"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        """Permisos: lectura para todos, crear para autenticados, otras acciones solo para admins"""
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):
        """Filtrar categorías según parámetros"""
        queryset = Category.objects.annotate(
            publications_count=Count('publication')
        )
        
        # Filtrar solo activas si no es admin
        if not (self.request.user.is_authenticated and 
                (self.request.user.is_staff or self.request.user.is_admin)):
            queryset = queryset.filter(is_active=True)
        
        # Filtro por búsqueda
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Filtro por estado activo
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')
    
    def get_serializer_class(self):
        """Usar serializer simplificado para listado"""
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    def perform_create(self, serializer):
        """Usuarios autenticados pueden sugerir categorías (inactivas), admins pueden crear activas"""
        # Los usuarios normales crean categorías como sugerencias (inactivas)
        # Los admins pueden crear categorías activas directamente
        serializer.save()
    
    def perform_update(self, serializer):
        """Solo administradores pueden actualizar categorías"""
        if not (self.request.user.is_staff or self.request.user.is_admin):
            raise PermissionError("Solo los administradores pueden actualizar categorías.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Solo administradores pueden eliminar categorías"""
        if not (self.request.user.is_staff or self.request.user.is_admin):
            raise PermissionError("Solo los administradores pueden eliminar categorías.")
        
        # Verificar que no tenga publicaciones asociadas
        publications_count = instance.publication_set.count()
        if publications_count > 0:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                f"No se puede eliminar una categoría que tiene {publications_count} publicaciones asociadas."
            )
        
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Obtener solo categorías activas"""
        active_categories = Category.objects.filter(is_active=True).annotate(
            publications_count=Count('publication')
        ).order_by('name')
        
        serializer = CategoryListSerializer(active_categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Activar/desactivar categoría (solo admins)"""
        if not (request.user.is_staff or request.user.is_admin):
            return Response({"error": "No tienes permisos para realizar esta acción"}, 
                          status=403)
        
        category = self.get_object()
        category.is_active = not category.is_active
        category.save()
        
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def suggested(self, request):
        """Obtener categorías sugeridas (inactivas) para revisión de admins"""
        if not (request.user.is_staff or request.user.is_admin):
            return Response({"error": "No tienes permisos para ver categorías sugeridas"}, 
                          status=403)
        
        suggested_categories = Category.objects.filter(is_active=False).annotate(
            publications_count=Count('publication')
        ).order_by('-created_at')
        
        serializer = CategorySerializer(suggested_categories, many=True)
        return Response(serializer.data)
