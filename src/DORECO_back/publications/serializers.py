from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Publication, Favorite
from categories.models import Category

User = get_user_model()


class PublicationSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Publication"""
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    keywords_list = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False
    )
    is_favorite = serializers.SerializerMethodField()
    favorites_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'description', 'category', 'category_name', 'condition',
            'publication_type', 'price', 'keywords', 'keywords_list', 'duration',
            'owner', 'owner_name', 'status', 'is_active', 'created_at', 'updated_at',
            'is_favorite', 'favorites_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner_name', 'category_name', 'is_favorite', 'favorites_count']

    def get_is_favorite(self, obj):
        """Verificar si la publicación es favorita del usuario actual"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, publication=obj).exists()
        return False

    def validate_category(self, value):
        if not value.is_active:
            raise serializers.ValidationError("No se puede asignar una categoría inactiva.")
        return value

    def validate_price(self, value):
        publication_type = self.initial_data.get('publication_type')
        if publication_type == 'sale' and (not value or value <= 0):
            raise serializers.ValidationError("El precio es requerido para publicaciones de venta.")
        elif publication_type in ['donation', 'loan'] and value:
            raise serializers.ValidationError("Las donaciones y préstamos no deben tener precio.")
        return value

    def validate_duration(self, value):
        publication_type = self.initial_data.get('publication_type')
        if publication_type == 'loan' and not value:
            raise serializers.ValidationError("La duración es requerida para préstamos.")
        return value

    def create(self, validated_data):
        keywords_list = validated_data.pop('keywords_list', [])
        if keywords_list:
            validated_data['keywords'] = ', '.join(keywords_list)
        
        # Asignar el usuario autenticado como propietario
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        keywords_list = validated_data.pop('keywords_list', None)
        if keywords_list is not None:
            validated_data['keywords'] = ', '.join(keywords_list)
        return super().update(instance, validated_data)


class PublicationListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar publicaciones"""
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_favorite = serializers.SerializerMethodField()
    
    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'condition', 'publication_type', 'price',
            'owner_name', 'category_name', 'status', 'created_at', 'is_favorite'
        ]
        read_only_fields = fields

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, publication=obj).exists()
        return False


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Favorite"""
    publication_title = serializers.CharField(source='publication.title', read_only=True)
    publication_type = serializers.CharField(source='publication.publication_type', read_only=True)
    owner_name = serializers.CharField(source='publication.owner.username', read_only=True)
    
    class Meta:
        model = Favorite
        fields = [
            'id', 'publication', 'publication_title', 'publication_type',
            'owner_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'publication_title', 'publication_type', 'owner_name']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user
        publication = attrs['publication']
        
        if Favorite.objects.filter(user=user, publication=publication).exists():
            raise serializers.ValidationError("Esta publicación ya está en tus favoritos.")
        
        if publication.owner == user:
            raise serializers.ValidationError("No puedes agregar tu propia publicación a favoritos.")
        
        return attrs


class MyPublicationsSerializer(serializers.ModelSerializer):
    """Serializer para las publicaciones del usuario autenticado"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    favorites_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'description', 'category_name', 'condition',
            'publication_type', 'price', 'status', 'is_active', 
            'created_at', 'updated_at', 'favorites_count'
        ]
        read_only_fields = fields 