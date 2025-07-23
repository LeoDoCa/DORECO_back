from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from .models import Publication, Favorite
from .serializers import (
    PublicationSerializer, PublicationListSerializer, FavoriteSerializer,
    MyPublicationsSerializer
)


class PublicationViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar publicaciones"""
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    
    def get_permissions(self):
        """Permisos: lectura para todos, escritura solo para autenticados"""
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):
        """Filtrar publicaciones según parámetros y usuario"""
        queryset = Publication.objects.select_related('owner', 'category').annotate(
            favorites_count=Count('favorites')
        )
        
        # Filtro base: solo publicaciones activas y disponibles para usuarios no autenticados
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_active=True, status='available')
        elif not (self.request.user.is_staff or self.request.user.is_admin):
            # Usuarios autenticados ven todas las activas
            queryset = queryset.filter(is_active=True)
        
        # Filtros de búsqueda
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(keywords__icontains=search)
            )
        
        # Filtro por categoría
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filtro por tipo de publicación
        publication_type = self.request.query_params.get('type', None)
        if publication_type:
            queryset = queryset.filter(publication_type=publication_type)
        
        # Filtro por condición
        condition = self.request.query_params.get('condition', None)
        if condition:
            queryset = queryset.filter(condition=condition)
        
        # Filtro por estado
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filtro por propietario
        owner = self.request.query_params.get('owner', None)
        if owner:
            queryset = queryset.filter(owner_id=owner)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action == 'list':
            return PublicationListSerializer
        elif self.action == 'my_publications':
            return MyPublicationsSerializer
        return PublicationSerializer
    
    def perform_update(self, serializer):
        """Solo el propietario o admin pueden actualizar"""
        publication = self.get_object()
        if not (self.request.user == publication.owner or 
                self.request.user.is_staff or self.request.user.is_admin):
            raise PermissionError("Solo puedes actualizar tus propias publicaciones.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Solo el propietario o admin pueden eliminar"""
        if not (self.request.user == instance.owner or 
                self.request.user.is_staff or self.request.user.is_admin):
            raise PermissionError("Solo puedes eliminar tus propias publicaciones.")
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def my_publications(self, request):
        """Obtener publicaciones del usuario autenticado"""
        publications = Publication.objects.filter(owner=request.user).annotate(
            favorites_count=Count('favorites')
        ).order_by('-created_at')
        
        serializer = MyPublicationsSerializer(publications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Agregar/quitar de favoritos"""
        publication = self.get_object()
        
        if publication.owner == request.user:
            return Response({"error": "No puedes agregar tu propia publicación a favoritos"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, 
            publication=publication
        )
        
        if not created:
            favorite.delete()
            return Response({"message": "Eliminado de favoritos", "is_favorite": False})
        else:
            return Response({"message": "Agregado a favoritos", "is_favorite": True})
    
    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        """Cambiar estado de la publicación"""
        publication = self.get_object()
        
        if not (request.user == publication.owner or 
                request.user.is_staff or request.user.is_admin):
            return Response({"error": "No tienes permisos para cambiar el estado"}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        if new_status not in ['available', 'reserved', 'completed', 'hidden']:
            return Response({"error": "Estado inválido"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        publication.status = new_status
        publication.save()
        
        serializer = PublicationSerializer(publication, context={'request': request})
        return Response(serializer.data)


class FavoriteViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar favoritos"""
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Solo favoritos del usuario autenticado"""
        return Favorite.objects.filter(user=self.request.user).select_related(
            'publication', 'publication__owner', 'publication__category'
        ).order_by('-created_at')
    
    def perform_destroy(self, instance):
        """Solo el propietario puede eliminar el favorito"""
        if instance.user != self.request.user:
            raise PermissionError("Solo puedes eliminar tus propios favoritos.")
        instance.delete()
    
    @action(detail=False, methods=['post'])
    def add_favorite(self, request):
        """Agregar publicación a favoritos"""
        publication_id = request.data.get('publication')
        if not publication_id:
            return Response({"error": "ID de publicación requerido"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            publication = Publication.objects.get(id=publication_id)
        except Publication.DoesNotExist:
            return Response({"error": "Publicación no encontrada"}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        if publication.owner == request.user:
            return Response({"error": "No puedes agregar tu propia publicación a favoritos"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, 
            publication=publication
        )
        
        if created:
            serializer = FavoriteSerializer(favorite, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Ya está en favoritos"}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    def remove_favorite(self, request):
        """Eliminar publicación de favoritos"""
        publication_id = request.data.get('publication')
        if not publication_id:
            return Response({"error": "ID de publicación requerido"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            favorite = Favorite.objects.get(user=request.user, publication_id=publication_id)
            favorite.delete()
            return Response({"message": "Eliminado de favoritos"})
        except Favorite.DoesNotExist:
            return Response({"error": "No está en favoritos"}, 
                          status=status.HTTP_404_NOT_FOUND)
