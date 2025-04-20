from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.shortcuts import get_object_or_404
from .serializers import GroupSerializer, PermissionSerializer, UserSerializer
from .models import GroupMetadata

User = get_user_model()

class IsStaff(permissions.BasePermission):
    """
    Permissão personalizada para verificar se o usuário é staff
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

class IsGroupAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas superusers ou o criador do grupo
    """
    def has_object_permission(self, request, view, obj):
        # Superusers podem fazer qualquer coisa
        if request.user.is_superuser:
            return True
            
        # Staff pode editar grupos que criou
        if request.user.is_staff:
            try:
                metadata = GroupMetadata.objects.get(group=obj)
                return metadata.created_by == request.user
            except GroupMetadata.DoesNotExist:
                return False
                
        return False

class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    
    def perform_create(self, serializer):
        """Cria o grupo e suas metadatas"""
        group = serializer.save()
        
        # Criar metadata do grupo
        description = self.request.data.get('description', '')
        GroupMetadata.objects.create(
            group=group,
            description=description,
            created_by=self.request.user
        )
        
        # Atribuir permissões se especificado
        permissions_data = self.request.data.get('permissions', [])
        if permissions_data:
            permissions = Permission.objects.filter(id__in=permissions_data)
            group.permissions.set(permissions)
        
        # Adicionar membros se especificado
        members_data = self.request.data.get('members', [])
        if members_data:
            users = User.objects.filter(id__in=members_data)
            for user in users:
                user.groups.add(group)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsStaff()]
        return [permissions.IsAuthenticated()]

class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    
    def perform_update(self, serializer):
        """Atualiza o grupo e suas metadatas"""
        group = serializer.save()
        
        # Atualizar descrição nas metadatas, se fornecida
        description = self.request.data.get('description')
        if description is not None:
            metadata, created = GroupMetadata.objects.get_or_create(
                group=group,
                defaults={'created_by': self.request.user}
            )
            metadata.description = description
            metadata.save()
            
        # Atualizar permissões se especificado
        permissions_data = self.request.data.get('permissions')
        if permissions_data is not None:
            permissions = Permission.objects.filter(id__in=permissions_data)
            group.permissions.set(permissions)
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsGroupAdmin()]
        return [permissions.IsAuthenticated()]

class GroupPermissionList(APIView):
    """
    Lista todos os grupos com suas permissões ou todas as permissões disponíveis
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Verificar se é uma solicitação para all_permissions
        if request.path.endswith('all_permissions/'):
            permissions_list = Permission.objects.all().order_by('content_type__model', 'name')
            permission_data = PermissionSerializer(permissions_list, many=True).data
            return Response(permission_data)
            
        # Caso contrário, retornar grupos com permissões
        groups = Group.objects.all()
        permissions_list = Permission.objects.all()

        group_data = GroupSerializer(groups, many=True).data
        permission_data = PermissionSerializer(permissions_list, many=True).data

        return Response({
            "groups": group_data,
            "permissions": permission_data
        })

class GroupMembersView(APIView):
    """
    Gerenciar membros de um grupo
    """
    def get_permissions(self):
        if self.request.method in ['PUT', 'POST', 'DELETE']:
            return [permissions.IsAuthenticated(), IsGroupAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        
        members = group.user_set.all()
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)
    
    def put(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        self.check_object_permissions(request, group)
        
        member_ids = request.data.get('members', [])
        
        # Limpar membros atuais
        group.user_set.clear()
        
        # Adicionar novos membros
        users = User.objects.filter(id__in=member_ids)
        for user in users:
            user.groups.add(group)
        
        return Response({'status': 'members updated'})
        
    def post(self, request, pk):
        """Compatibilidade com o método users do ViewSet anterior"""
        group = get_object_or_404(Group, pk=pk)
        self.check_object_permissions(request, group)
        
        users_ids = request.data.get('users_ids', [])
        users = User.objects.filter(id__in=users_ids)
        
        # Atualizar o grupo com os novos usuários
        group.user_set.set(users)
        
        return Response(status=204)

class GroupPermissionsView(APIView):
    """
    Gerenciar permissões de um grupo
    """
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE', 'POST']:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def get(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        
        # Se for para o endpoint group_permissions, retorna apenas IDs
        if request.path.endswith('group_permissions/'):
            permissions = group.permissions.all()
            data = [perm.id for perm in permissions]
            return Response(data)
        
        # Caso contrário, retorna detalhes completos
        permissions = group.permissions.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)
    
    def put(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        self.check_object_permissions(request, group)
        
        permission_ids = request.data.get('permissions', [])
        
        # Limpar permissões atuais
        group.permissions.clear()
        
        # Adicionar novas permissões
        permissions = Permission.objects.filter(id__in=permission_ids)
        group.permissions.set(permissions)
        
        return Response({'status': 'permissions updated'})
        
    def post(self, request, pk):
        """Compatibilidade com o método update_permissions do ViewSet anterior"""
        group = get_object_or_404(Group, pk=pk)
        self.check_object_permissions(request, group)
        
        permission_ids = request.data.get('permissions', [])
        
        # Limpar permissões atuais
        group.permissions.clear()
        
        # Adicionar novas permissões
        permissions = Permission.objects.filter(id__in=permission_ids)
        group.permissions.set(permissions)
        
        return Response(status=status.HTTP_200_OK)

class UserPermissionView(APIView):
    """
    Verificar se um usuário tem uma permissão específica
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id, permission_codename):
        # Apenas o próprio usuário ou admin pode verificar permissões
        if request.user.id != int(user_id) and not request.user.is_superuser:
            return Response({"detail": "Não autorizado"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_object_or_404(User, id=user_id)
        has_permission = user.has_perm(permission_codename)
        
        return Response({"has_permission": has_permission})

class UserPermissionsView(APIView):
    """
    Listar todas as permissões de um usuário
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id):
        # Apenas o próprio usuário ou admin pode verificar permissões
        if request.user.id != int(user_id) and not request.user.is_superuser:
            return Response({"detail": "Não autorizado"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_object_or_404(User, id=user_id)
        
        # Coletar todas as permissões do usuário
        permissions_set = set()
        
        # Permissões diretas do usuário
        for perm in user.user_permissions.all():
            permissions_set.add(perm)
        
        # Permissões através de grupos
        for group in user.groups.all():
            for perm in group.permissions.all():
                permissions_set.add(perm)
        
        serializer = PermissionSerializer(list(permissions_set), many=True)
        return Response(serializer.data)

class GroupDebugView(APIView):
    """
    Endpoint de depuração para verificar o funcionamento da API
    """
    def get(self, request):
        try:
            groups = Group.objects.all()
            return Response({
                "count": groups.count(),
                "names": [g.name for g in groups],
                "request_path": request.path,
                "auth": str(request.user)
            })
        except Exception as e:
            return Response({
                "error": str(e),
                "type": type(e).__name__
            }, status=500)
        
class CheckGroupName(APIView):
    """
    Verifica se um nome de grupo já existe
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        name = request.query_params.get('name', '')
        if not name:
            return Response(
                {"error": "O parâmetro 'name' é obrigatório"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        exists = Group.objects.filter(name__iexact=name).exists()
        return Response({"exists": exists})