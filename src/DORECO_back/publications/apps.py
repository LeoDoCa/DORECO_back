from django.apps import AppConfig


class PublicationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'publications'

    def ready(self):
        from django.db.models.signals import post_migrate
        from django.dispatch import receiver
        from django.apps import apps
        from django.core.files.base import ContentFile
        import io
        from PIL import Image

        @receiver(post_migrate)
        def create_default_publication(sender, **kwargs):
            if sender.name not in ('publications', 'DORECO_back.publications'):
                return
                
            try:
                Publication = apps.get_model('publications', 'Publication')
                CustomUser = apps.get_model('users', 'CustomUser')
                Category = apps.get_model('categories', 'Category')

                # Solo crear datos de ejemplo si no existen publicaciones
                if Publication.objects.exists():
                    return

                # Obtener el usuario normal creado en users.apps
                normal_user = CustomUser.objects.filter(email='user@example.com').first()
                
                if normal_user:
                    # Crear una categoría por defecto si no existe
                    category, _ = Category.objects.get_or_create(
                        name='General',
                        defaults={'description': 'Categoría general para publicaciones'}
                    )

                    # Crear publicación de ejemplo si no existe
                    if not Publication.objects.filter(title='Mi primera publicación').exists():
                        try:
                            # Crear una imagen simple en memoria para la publicación
                            img = Image.new('RGB', (300, 300), color='lightblue')
                            img_io = io.BytesIO()
                            img.save(img_io, format='JPEG', quality=85)
                            img_content = ContentFile(img_io.getvalue(), 'default_publication.jpg')
                            
                            Publication.objects.create(
                                title='Mi primera publicación',
                                description='Esta es una publicación de ejemplo creada por un usuario normal',
                                keywords='ejemplo, usuario, normal',
                                condition='good',  # Campo requerido
                                publication_type='donation',  # Campo requerido
                                owner=normal_user,
                                category=category,
                                status='available',
                                is_active=True,
                                image1=img_content  # Campo requerido
                            )
                            print("✅ Publicación de ejemplo creada exitosamente")
                        except Exception as e:
                            print(f"⚠️ No se pudo crear la publicación de ejemplo: {e}")
                            # No es crítico, continúa sin la publicación de ejemplo
                            pass
                            
            except Exception as e:
                print(f"⚠️ Error en post_migrate de publications: {e}")
                # No es crítico para las migraciones, solo es para datos de ejemplo
                pass