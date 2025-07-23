from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SystemStats, AdminAction

User = get_user_model()


class SystemStatsSerializer(serializers.ModelSerializer):
    """Serializer para el modelo SystemStats"""
    completion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemStats
        fields = [
            'id', 'date', 'total_publications', 'total_donations', 'total_loans',
            'total_sales', 'completed_donations', 'completed_loans', 'completed_sales',
            'active_users', 'new_users', 'completion_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completion_rate']

    def get_completion_rate(self, obj):
        """Calcular tasa de finalización general"""
        total_completed = obj.completed_donations + obj.completed_loans + obj.completed_sales
        total_publications = obj.total_publications
        
        if total_publications > 0:
            return round((total_completed / total_publications) * 100, 2)
        return 0.0

    def validate_date(self, value):
        """Validar que no existan estadísticas duplicadas para la misma fecha"""
        if self.instance and self.instance.date == value:
            return value
        
        if SystemStats.objects.filter(date=value).exists():
            raise serializers.ValidationError("Ya existen estadísticas para esta fecha.")
        return value


class AdminActionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo AdminAction"""
    admin_username = serializers.CharField(source='admin_user.username', read_only=True)
    admin_name = serializers.CharField(source='admin_user.name', read_only=True)
    
    class Meta:
        model = AdminAction
        fields = [
            'id', 'admin_user', 'admin_username', 'admin_name', 'action_type',
            'target_id', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'admin_user', 'admin_username', 'admin_name', 'created_at']

    def create(self, validated_data):
        validated_data['admin_user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_admin_user(self, value):
        """Validar que el usuario sea administrador"""
        if not value.is_staff and not value.is_admin:
            raise serializers.ValidationError("Solo los administradores pueden realizar acciones administrativas.")
        return value


class AdminActionCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear acciones administrativas"""
    
    class Meta:
        model = AdminAction
        fields = ['action_type', 'target_id', 'description']

    def create(self, validated_data):
        validated_data['admin_user'] = self.context['request'].user
        return super().create(validated_data)


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas del dashboard"""
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    total_publications = serializers.IntegerField()
    pending_reports = serializers.IntegerField()
    completed_transactions = serializers.IntegerField()
    recent_stats = SystemStatsSerializer(many=True)


class AdminActionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar acciones administrativas"""
    admin_username = serializers.CharField(source='admin_user.username', read_only=True)
    
    class Meta:
        model = AdminAction
        fields = [
            'id', 'admin_username', 'action_type', 'target_id', 'created_at'
        ]
        read_only_fields = fields


class SystemStatsCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear estadísticas del sistema"""
    
    class Meta:
        model = SystemStats
        fields = [
            'date', 'total_publications', 'total_donations', 'total_loans',
            'total_sales', 'completed_donations', 'completed_loans', 'completed_sales',
            'active_users', 'new_users'
        ]

    def validate_date(self, value):
        if SystemStats.objects.filter(date=value).exists():
            raise serializers.ValidationError("Ya existen estadísticas para esta fecha.")
        return value 