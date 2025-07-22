from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch.dispatcher import receiver
from django.utils.timezone import now
from django.core.validators import RegexValidator, MinLengthValidator, EmailValidator, FileExtensionValidator


@receiver(user_logged_in)
def update_last_login(sender, user, **kwargs):
    user.last_login = now()
    user.save()

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=60, blank=False, null=False, validators=[
            MinLengthValidator(2, "El nombre debe tener al menos 2 caracteres"),
            RegexValidator(
                regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$',
                message="El nombre solo puede contener letras y espacios"
            )
        ])
    surnames = models.CharField(max_length=80, blank=False, null=False, validators=[
            MinLengthValidator(2, "Los apellidos deben tener al menos 2 caracteres"),
            RegexValidator(
                regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$',
                message="Los apellidos solo pueden contener letras y espacios"
            )
        ])
    email = models.EmailField(
        unique=True, 
        blank=False, 
        null=False, 
        validators=[EmailValidator(message="Ingrese un correo electrónico válido")],
        error_messages={'unique': 'Ya existe un usuario con este correo electrónico'}
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Número de teléfono inválido')]
    )
    username = models.CharField(max_length=45, blank=False, null=False, unique=True, validators=[
            MinLengthValidator(3, "El nombre de usuario debe tener al menos 3 caracteres"),
            RegexValidator(
                regex=r'^[a-zA-Z][a-zA-Z0-9_-]*$',
                message="El nombre de usuario debe comenzar con una letra y solo puede contener letras, números, guiones y guiones bajos"
            )
        ],
        error_messages={
            'unique': 'Este nombre de usuario ya está en uso'
        })
    token = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(
        upload_to="user", 
        default="default.png", 
        blank=True, 
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif'],
                message="Solo se permiten archivos de imagen en formato JPG, JPEG, PNG o GIF"
            )
        ]
    )
    role = models.ForeignKey("Role", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.BooleanField(default=True, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, blank=False, null=False)
    is_staff = models.BooleanField(default=False, blank=False, null=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surnames"]

    def __str__(self):
        return self.email

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"


class Role(models.Model):
    name = models.CharField(
        max_length=45, 
        blank=False, 
        null=False, 
        unique=True, 
        validators=[MinLengthValidator(2, "El nombre del rol debe tener al menos 2 caracteres")]
    )
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = "role"
        verbose_name = "Role"
        verbose_name_plural = "Roles"