# Asegura la creación de roles y usuarios por defecto al iniciar la app
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from django.db.models.signals import post_migrate
        from django.dispatch import receiver
        from django.utils.timezone import now
        from django.apps import apps

        @receiver(post_migrate)
        def create_default_roles_and_users(sender, **kwargs):
            if sender.name not in ('users', 'DORECO_back.users'):
                return
            Role = apps.get_model('users', 'Role')
            CustomUser = apps.get_model('users', 'CustomUser')
            admin_role, _ = Role.objects.get_or_create(name='ADMIN')
            user_role, _ = Role.objects.get_or_create(name='USER')
            if not CustomUser.objects.filter(email='admin@example.com').exists():
                CustomUser.objects.create_superuser(
                    email='admin@example.com',
                    password='admin1234',
                    name='Admin',
                    surnames='User',
                    username='admin',
                    role=admin_role,
                    is_admin=True
                )
            if not CustomUser.objects.filter(email='user@example.com').exists():
                CustomUser.objects.create_user(
                    email='user@example.com',
                    password='user1234',
                    name='Normal',
                    surnames='User',
                    username='user',
                    role=user_role
                )

