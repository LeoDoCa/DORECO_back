import uuid
from django.db import models
from django.conf import settings
from categories.models import Category

class Publication(models.Model):
    TYPE_CHOICES = [
        ('donation', 'Donación'),
        ('loan', 'Préstamo'),
        ('sale', 'Venta'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('reserved', 'Reservado'),
        ('completed', 'Completado'),
        ('hidden', 'Oculto'),
    ]
    
    CONDITION_CHOICES = [
        ('new', 'Nuevo'),
        ('like_new', 'Como nuevo'),
        ('good', 'Bueno'),
        ('fair', 'Regular'),
        ('poor', 'Malo'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    publication_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    keywords = models.CharField(max_length=500, help_text="Palabras clave separadas por comas")
    duration = models.PositiveSmallIntegerField(help_text="Duración del préstamo o disponibilidad", null=True, blank=True)
    
    # Relaciones
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='publications')

    # Imágenes (hasta 3)
    image1 = models.ImageField(upload_to='publications/', null=False, blank=False)
    image2 = models.ImageField(upload_to='publications/', null=True, blank=True)
    image3 = models.ImageField(upload_to='publications/', null=True, blank=True)
    
    # Estados
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_active = models.BooleanField(default=True)
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_publication_type_display()}"
    
    def get_keywords_list(self):
        return [keyword.strip() for keyword in self.keywords.split(',') if keyword.strip()]


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'publication']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.publication.title}"
