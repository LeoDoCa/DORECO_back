from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.utils import timezone
import uuid
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def generate_password_reset_token(user):
    """
    Genera un token de recuperación de contraseña para el usuario
    """
    # Generar token y establecer expiración
    token = user.generate_password_reset_token()
    return token


def send_password_reset_email(user, token, request=None):
    """
    Envía email de recuperación de contraseña al usuario
    """
    try:
        # Construir URL de reset - siempre apuntar al frontend React
        frontend_domain = getattr(settings, 'FRONTEND_DOMAIN', 'localhost:3000')
        frontend_protocol = getattr(settings, 'FRONTEND_PROTOCOL', 'http')
        
        reset_url = f"{frontend_protocol}://{frontend_domain}/reset-password?token={token}"
        
        # Preparar contexto para el template
        context = {
            'user': user,
            'reset_url': reset_url,
            'token': token,
            'expiry_hours': 1,
        }
        
        # Renderizar templates
        html_content = render_to_string('email/password_reset.html', context)
        text_content = render_to_string('email/password_reset.txt', context)
        
        # Crear y enviar email
        subject = 'DORECO - Recuperación de Contraseña'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to_email
        )
        email.attach_alternative(html_content, "text/html")
        
        email.send()
        
        logger.info(f"Password reset email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending password reset email to {user.email}: {str(e)}")
        return False


def create_and_send_password_reset(user, request=None):
    """
    Crea token y envía email de recuperación de contraseña
    Función de conveniencia que combina ambas operaciones
    """
    try:
        # Generar token
        token = generate_password_reset_token(user)
        
        # Enviar email
        email_sent = send_password_reset_email(user, token, request)
        
        if email_sent:
            logger.info(f"Password reset process completed for user {user.email}")
            return True, "Email de recuperación enviado exitosamente"
        else:
            logger.error(f"Failed to send password reset email for user {user.email}")
            return False, "Error al enviar el email de recuperación"
            
    except Exception as e:
        logger.error(f"Error in password reset process for user {user.email}: {str(e)}")
        return False, f"Error en el proceso de recuperación: {str(e)}"


def cleanup_expired_tokens():
    """
    Limpia tokens expirados de la base de datos
    Esta función puede ser llamada periódicamente
    """
    try:
        from .models import CustomUser
        
        expired_users = CustomUser.objects.filter(
            token__isnull=False,
            token_expires_at__lt=timezone.now()
        )
        
        count = expired_users.count()
        expired_users.update(token=None, token_expires_at=None)
        
        logger.info(f"Cleaned up {count} expired password reset tokens")
        return count
        
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {str(e)}")
        return 0 