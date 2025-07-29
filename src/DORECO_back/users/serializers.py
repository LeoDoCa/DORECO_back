from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import CustomUser, Role


class RoleSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Role"""
    
    class Meta:
        model = Role
        fields = ['id', 'name']
        read_only_fields = ['id']

    def validate_name(self, value):
        if Role.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un rol con este nombre.")
        return value


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo CustomUser"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'name', 'surnames', 'email', 'phone_number', 'username', 
            'photo', 'role', 'role_name', 'status', 'created_at', 'updated_at', 
            'is_admin', 'is_active', 'is_staff', 'password', 'password_confirm'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'role_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirm': {'write_only': True},
        }

    def validate(self, attrs):
        if 'password' in attrs and 'password_confirm' in attrs:
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError("Las contraseñas no coinciden.")
        return attrs

    def validate_email(self, value):
        if self.instance and self.instance.email == value:
            return value
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value

    def validate_username(self, value):
        if self.instance and self.instance.username == value:
            return value
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este nombre de usuario.")
        return value

    def create(self, validated_data):
        from .models import Role
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        # Asignar siempre el rol USER (id=2)
        try:
            user_role = Role.objects.get(id=2)
        except Role.DoesNotExist:
            raise serializers.ValidationError("El rol USER (id=2) no existe en la base de datos.")
        validated_data['role'] = user_role
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):
    """Serializer para login de usuario"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Credenciales inválidas.")
            if not user.is_active:
                raise serializers.ValidationError("La cuenta de usuario está desactivada.")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("Email y contraseña son requeridos.")
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer simplificado para el perfil del usuario"""
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'name', 'surnames', 'email', 'phone_number', 'username', 
            'photo', 'role_name', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'created_at', 'role_name']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Las nuevas contraseñas no coinciden.")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value 