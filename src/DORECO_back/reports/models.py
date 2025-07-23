from django.db import models
from django.conf import settings
from publications.models import Publication

class Report(models.Model):
    REASON_CHOICES = [
        ('inappropriate', 'Contenido inapropiado'),
        ('spam', 'Spam'),
        ('fake', 'Información falsa'),
        ('duplicate', 'Duplicado'),
        ('other', 'Otro'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('reviewed', 'Revisado'),
        ('resolved', 'Resuelto'),
        ('dismissed', 'Desestimado'),
    ]
    
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Administración
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reports_reviewed'
    )
    admin_comment = models.TextField(blank=True, null=True)
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['publication', 'reported_by']
    
    def __str__(self):
        return f"Reporte: {self.publication.title} por {self.reported_by.username}"