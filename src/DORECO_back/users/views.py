from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.db.models import Q
from .models import CustomUser, Role
from .serializers import (
    CustomUserSerializer, RoleSerializer, UserLoginSerializer,
    UserProfileSerializer, ChangePasswordSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from .utils import create_and_send_password_reset


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar roles"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Solo admins pueden crear, actualizar y eliminar roles"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated]
            # Validación adicional en el método
        return super().get_permissions()
    
    def perform_create(self, serializer):
        if not (self.request.user.is_staff or self.request.user.is_admin):
            raise PermissionError("Solo los administradores pueden crear roles.")
        serializer.save()
    
    def perform_update(self, serializer):
        if not (self.request.user.is_staff or self.request.user.is_admin):
            raise PermissionError("Solo los administradores pueden actualizar roles.")
        serializer.save()
    
    def perform_destroy(self, instance):
        if not (self.request.user.is_staff or self.request.user.is_admin):
            raise PermissionError("Solo los administradores pueden eliminar roles.")
        instance.delete()


class CustomUserViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar usuarios"""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas generales para dashboard"""
        from publications.models import Publication
        from reports.models import Report
        from .models import CustomUser
        total_users = CustomUser.objects.count()
        total_active_publications = Publication.objects.filter(is_active=True).count()
        total_sold = Publication.objects.filter(publication_type='sale').count()
        total_loaned = Publication.objects.filter(publication_type='loan').count()
        total_donated = Publication.objects.filter(publication_type='donation').count()
        pending_reports = Report.objects.filter(status='pending').count()
        return Response({
            "total_users": total_users,
            "total_active_publications": total_active_publications,
            "total_sold": total_sold,
            "total_loaned": total_loaned,
            "total_donated": total_donated,
            "pending_reports": pending_reports,
        })
    
    def get_permissions(self):
        """Permisos específicos por acción"""
        if self.action in ['create', 'register', 'login', 'password_reset_request', 'password_reset_confirm', 'verify_reset_token']:
            self.permission_classes = [AllowAny]
        elif self.action in ['list', 'destroy']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):
        """Filtrar queryset según el usuario"""
        if self.request.user.is_staff or self.request.user.is_admin:
            return CustomUser.objects.all()
        # Usuarios normales solo ven su propio perfil
        return CustomUser.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action in ['profile', 'update_profile']:
            return UserProfileSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return CustomUserSerializer
    
    def perform_destroy(self, instance):
        """Solo admins pueden eliminar usuarios o usuarios pueden eliminarse a sí mismos"""
        if not (self.request.user.is_staff or self.request.user.is_admin or self.request.user == instance):
            raise PermissionError("No tienes permisos para eliminar este usuario.")
        instance.delete()
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """Endpoint para login de usuarios"""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserProfileSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Endpoint para registrar nuevos usuarios"""
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserProfileSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Endpoint para logout"""
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout exitoso"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Obtener perfil del usuario autenticado"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Actualizar perfil del usuario autenticado"""
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Cambiar contraseña del usuario autenticado"""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Cambiar la contraseña
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Contraseña cambiada exitosamente"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Buscar usuarios (solo para admins)"""
        if not (request.user.is_staff or request.user.is_admin):
            return Response({"error": "No tienes permisos para realizar búsquedas"}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        query = request.query_params.get('q', '')
        if query:
            users = CustomUser.objects.filter(
                Q(name__icontains=query) | 
                Q(surnames__icontains=query) | 
                Q(username__icontains=query) |
                Q(email__icontains=query)
            )
            serializer = UserProfileSerializer(users, many=True)
            return Response(serializer.data)
        return Response([])
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def password_reset_request(self, request):
        """Solicitar recuperación de contraseña por email"""
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.get(email=email, is_active=True)
            
            # Crear token y enviar email
            success, message = create_and_send_password_reset(user, request)
            
            if success:
                return Response({
                    "message": "Si el correo electrónico existe en nuestro sistema, recibirás un enlace de recuperación."
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "Hubo un problema al enviar el email. Inténtalo de nuevo más tarde."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def password_reset_confirm(self, request):
        """Confirmar y cambiar contraseña con token"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Contraseña restablecida exitosamente. Ya puedes iniciar sesión con tu nueva contraseña."
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def verify_reset_token(self, request):
        """Verificar si un token de reset es válido"""
        token = request.query_params.get('token')
        if not token:
            return Response({
                "error": "Token es requerido"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(token=token)
            if user.is_token_valid():
                return Response({
                    "valid": True,
                    "user_email": user.email,
                    "expires_at": user.token_expires_at
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "valid": False,
                    "error": "El token ha expirado o ya fue utilizado"
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except CustomUser.DoesNotExist:
            return Response({
                "valid": False,
                "error": "Token inválido"
            }, status=status.HTTP_400_BAD_REQUEST)
