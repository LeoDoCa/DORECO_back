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
        """Permisos: lectura para todos, escritura solo para admins"""
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
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
        """Solo administradores pueden crear categorías"""
        if not (self.request.user.is_staff or self.request.user.is_admin):
            raise PermissionError("Solo los administradores pueden crear categorías.")
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
        if instance.publication_set.exists():
            raise ValueError("No se puede eliminar una categoría que tiene publicaciones asociadas.")
        
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
