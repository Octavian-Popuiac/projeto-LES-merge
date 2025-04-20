from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from .models import GroupMetadata

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class PermissionSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type', 'description', 'category']
    
    def get_description(self, obj):
        descriptions = {
            'add_group': 'Permite adicionar novos grupos',
            'change_group': 'Permite editar grupos existentes',
            'delete_group': 'Permite excluir grupos',
            'view_group': 'Permite visualizar grupos',
            # Adicione mais mapeamentos conforme necessário
        }
        return descriptions.get(obj.codename, '')
    
    def get_category(self, obj):
        return obj.content_type.model if obj.content_type else 'outros'

class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    members = UserSerializer(source='user_set', many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    created_by_id = serializers.SerializerMethodField()
    description = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'members', 'member_count', 
                 'created_by', 'created_by_id', 'description']
    
    def get_member_count(self, obj):
        return obj.user_set.count()
    
    def get_created_by(self, obj):
        try:
            metadata = GroupMetadata.objects.get(group=obj)
            if metadata.created_by:
                return metadata.created_by.username
        except GroupMetadata.DoesNotExist:
            pass
        return None
    
    def get_created_by_id(self, obj):
        try:
            metadata = GroupMetadata.objects.get(group=obj)
            if metadata.created_by:
                return metadata.created_by.id
        except GroupMetadata.DoesNotExist:
            pass
        return None
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Adicionar descrição do metadata se existir
        try:
            metadata = GroupMetadata.objects.get(group=instance)
            data['description'] = metadata.description
        except GroupMetadata.DoesNotExist:
            data['description'] = ''
        return data
    
    def create(self, validated_data):
        description = validated_data.pop('description', '')
        
        # Criar o grupo
        group = Group.objects.create(**validated_data)
        
        # Nota: A criação da metadata é feita na view perform_create
        # para ter acesso ao request.user
        
        return group
        
    def update(self, instance, validated_data):
        description = validated_data.pop('description', None)
        
        # Atualizar campos básicos do grupo
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        
        # Nota: A atualização da metadata é feita na view perform_update
        # para ter acesso ao request.user
            
        return instance