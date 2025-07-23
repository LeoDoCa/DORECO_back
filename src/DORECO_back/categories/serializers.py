from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer para el modelo Category"""
    publications_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'publications_count']
        read_only_fields = ['id', 'created_at', 'publications_count']

    def validate_name(self, value):
        if self.instance and self.instance.name == value:
            return value
        if Category.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Ya existe una categoría con este nombre.")
        return value


class CategoryListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar categorías"""
    publications_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active', 'publications_count']
        read_only_fields = ['id', 'publications_count'] 