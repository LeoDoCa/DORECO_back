from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Publication, Favorite
from categories.models import Category

User = get_user_model()


class PublicationSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Publication"""
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    owner_photo = serializers.ImageField(source='owner.photo', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    keywords_list = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False
    )
    is_favorite = serializers.SerializerMethodField()
    favorites_count = serializers.IntegerField(read_only=True)
    image1 = serializers.ImageField(required=True)
    image2 = serializers.ImageField(required=False, allow_null=True)
    image3 = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'description', 'category', 'category_name', 'condition',
            'publication_type', 'price', 'keywords', 'keywords_list', 'duration',
            'owner', 'owner_name', 'owner_photo', 'status', 'is_active', 'created_at', 'updated_at',
            'is_favorite', 'favorites_count',
            'image1', 'image2', 'image3',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner', 'owner_name', 'owner_photo', 'category_name', 'is_favorite', 'favorites_count']

    def get_is_favorite(self, obj):
        """Verificar si la publicación es favorita del usuario actual"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, publication=obj).exists()
        return False

    def validate(self, attrs):
        images = [attrs.get('image1'), attrs.get('image2'), attrs.get('image3')]
        images = [img for img in images if img]
        if len(images) < 1:
            raise serializers.ValidationError("Debes subir al menos una imagen.")
        if len(images) > 3:
            raise serializers.ValidationError("No puedes subir más de 3 imágenes.")
        return attrs

    def validate_category(self, value):
        # Permitir uso de categorías inactivas (sugeridas por usuarios)
        # La validación se hará en el negocio si es necesario
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
        validated_data['owner'] = self.context['request'].user
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        keywords_list = validated_data.pop('keywords_list', None)
        if keywords_list is not None:
            validated_data['keywords'] = ', '.join(keywords_list)
        
        validated_data.pop('owner', None)
        for img_field in ['image1', 'image2', 'image3']:
            if img_field in validated_data:
                setattr(instance, img_field, validated_data[img_field])
        
        instance.save()
        return instance


class PublicationUpdateSerializer(serializers.ModelSerializer):
    """Serializer específico para actualizar publicaciones"""
    keywords_list = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Publication
        fields = [
            'title', 'description', 'category', 'condition',
            'publication_type', 'price', 'keywords', 'keywords_list', 'duration',
            'status', 'is_active'
        ]

    def validate_price(self, value):
        publication_type = self.initial_data.get('publication_type', self.instance.publication_type)
        if publication_type == 'sale' and (not value or value <= 0):
            raise serializers.ValidationError("El precio es requerido para publicaciones de venta.")
        elif publication_type in ['donation', 'loan'] and value:
            raise serializers.ValidationError("Las donaciones y préstamos no deben tener precio.")
        return value

    def validate_duration(self, value):
        publication_type = self.initial_data.get('publication_type', self.instance.publication_type)
        if publication_type == 'loan' and not value:
            raise serializers.ValidationError("La duración es requerida para préstamos.")
        return value

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
            'id', 'title', 'description', 'condition', 'publication_type', 'price',
            'duration', 'keywords','is_active',
            'owner_name', 'category_name', 'status', 'created_at', 'is_favorite',
            'image1', 'image2', 'image3'
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
    publication_data = PublicationListSerializer(source="publication", read_only=True)
    
    class Meta:
        model = Favorite
        fields = [
            'id', 'publication', 'publication_title', 'publication_type',
            'owner_name', 'created_at', 'publication_data'
        ]
        read_only_fields = ['id', 'created_at', 'publication_title', 'publication_type', 'owner_name', 'publication_data']

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
            'id', 'title', 'description', 'category_name', 'condition', 'image1',
            'publication_type', 'price', 'status', 'is_active', 
            'created_at', 'updated_at', 'favorites_count'
        ]
        read_only_fields = fields


class SendMessageSerializer(serializers.Serializer):
    """Serializer para validar los datos del mensaje enviado al propietario de una publicación"""
    message = serializers.CharField(
        max_length=1000, 
        help_text="Mensaje a enviar al propietario de la publicación"
    )
    
    def validate_message(self, value):
        """Validar que el mensaje no esté vacío y tenga contenido útil"""
        if not value or not value.strip():
            raise serializers.ValidationError("El mensaje no puede estar vacío.")
        if len(value.strip()) < 10:
            raise serializers.ValidationError("El mensaje debe tener al menos 10 caracteres.")
        return value.strip() 