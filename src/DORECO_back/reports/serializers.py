from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Report
from publications.models import Publication

User = get_user_model()


class ReportSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Report"""
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    publication_title = serializers.CharField(source='publication.title', read_only=True)
    publication_owner = serializers.CharField(source='publication.owner.username', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'publication', 'publication_title', 'publication_owner',
            'reported_by', 'reported_by_username', 'reason', 'description',
            'status', 'reviewed_by', 'reviewed_by_username', 'admin_comment',
            'created_at'
        ]
        read_only_fields = [
            'id', 'reported_by', 'reported_by_username', 'publication_title',
            'publication_owner', 'reviewed_by', 'reviewed_by_username', 'created_at'
        ]

    def create(self, validated_data):
        validated_data['reported_by'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user
        publication = attrs['publication']
        
        # Verificar que el usuario no reporte su propia publicación
        if publication.owner == user:
            raise serializers.ValidationError("No puedes reportar tu propia publicación.")
        
        # Verificar que no haya reportado ya esta publicación
        if Report.objects.filter(reported_by=user, publication=publication).exists():
            raise serializers.ValidationError("Ya has reportado esta publicación.")
        
        return attrs


class CreateReportSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear reportes"""
    
    class Meta:
        model = Report
        fields = ['publication', 'reason', 'description']

    def create(self, validated_data):
        validated_data['reported_by'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user
        publication = attrs['publication']
        
        if publication.owner == user:
            raise serializers.ValidationError("No puedes reportar tu propia publicación.")
        
        if Report.objects.filter(reported_by=user, publication=publication).exists():
            raise serializers.ValidationError("Ya has reportado esta publicación.")
        
        return attrs


class AdminReportSerializer(serializers.ModelSerializer):
    """Serializer para administradores para gestionar reportes"""
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    publication_title = serializers.CharField(source='publication.title', read_only=True)
    publication_owner = serializers.CharField(source='publication.owner.username', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'publication', 'publication_title', 'publication_owner',
            'reported_by_username', 'reason', 'description', 'status',
            'reviewed_by_username', 'admin_comment', 'created_at'
        ]
        read_only_fields = [
            'id', 'publication', 'publication_title', 'publication_owner',
            'reported_by_username', 'reason', 'description', 'reviewed_by_username',
            'created_at'
        ]

    def update(self, instance, validated_data):
        # Asignar el usuario actual como reviewer si se cambia el estado
        if 'status' in validated_data and validated_data['status'] != instance.status:
            validated_data['reviewed_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class ReportListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar reportes"""
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    publication_title = serializers.CharField(source='publication.title', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'publication_title', 'reported_by_username', 'reason',
            'status', 'created_at'
        ]
        read_only_fields = fields 