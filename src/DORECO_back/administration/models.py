from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class SystemStats(models.Model):
    """Modelo para almacenar estadísticas del sistema"""
    date = models.DateField(unique=True)
    total_publications = models.IntegerField(default=0)
    total_donations = models.IntegerField(default=0)
    total_loans = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)
    completed_donations = models.IntegerField(default=0)
    completed_loans = models.IntegerField(default=0)
    completed_sales = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "System Statistics"
        ordering = ['-date']
    
    def __str__(self):
        return f"Estadísticas del {self.date}"

class AdminAction(models.Model):
    """Modelo para registrar acciones administrativas"""
    ACTION_TYPES = [
        ('delete_publication', 'Eliminar publicación'),
        ('ban_user', 'Banear usuario'),
        ('approve_category', 'Aprobar categoría'),
        ('reject_category', 'Rechazar categoría'),
        ('resolve_report', 'Resolver reporte'),
    ]
    
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    target_id = models.CharField(max_length=100)  # ID del objeto afectado
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.get_action_type_display()}"