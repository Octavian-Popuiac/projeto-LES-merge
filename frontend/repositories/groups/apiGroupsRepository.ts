import { GroupRepository } from "~/domain/models/groups/groupRepository";
import { GroupItem, GroupItemList } from "~/domain/models/groups/groups";
import { CustomPermission, Permission} from "~/domain/models/permissions/permissions";
import ApiService from "~/services/api.service";

export class APIGroupRepository implements GroupRepository {
  constructor(private readonly apiService = ApiService) {}

  async getGroups(): Promise<GroupItemList> {
      const response = await this.apiService.get('/groups/')
      return response.data;
  }
  
  async getGroup(id: number): Promise<GroupItem> {
    const response = await this.apiService.get(`/groups/${id}/`);
    return response.data;
  }

  async getGroupMembers(id: number): Promise<any[]> {
    const response = await this.apiService.get(`/groups/${id}/users/`);
    return response.data;
  }

  async updateGroup(id: number, data: {name: string, description?: string}): Promise<GroupItem> {
    const response = await this.apiService.put(`/groups/${id}/`, data);
    return response.data;
  }

  async deleteGroup(id: number): Promise<void> {
    await this.apiService.delete(`/groups/${id}/`);
  }

  async addUsersToGroup(groupId: number, userIds: number[]): Promise<void> {
    await this.apiService.post(`/groups/${groupId}/users/`, { users_ids: userIds });
  }

  async removeUserFromGroup(groupId: number, userId: number): Promise<void> {
    await this.apiService.delete(`/groups/${groupId}/users/${userId}/`);
  }

  async getAllPermissions(): Promise<Permission[]> {
    try{
      const response = await this.apiService.get('/groups/all_permissions/');
      return response.data.map((item: CustomPermission) => new Permission(item))
    }catch(error){
      console.error('Error fetching permissions:', error);
      throw error;
    }
  }
  
  async getGroupPermissions(groupId: number): Promise<number[]> {
    try {
      const response = await this.apiService.get(`/groups/${groupId}/group_permissions/`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar permissões do grupo:', error);
      throw error;
    }
  }
  
  async updateGroupPermissions(groupId: number, permissionIds: number[]): Promise<void> {
    await this.apiService.post(`/groups/${groupId}/permissions/`, {
      permissions: permissionIds
    });
  }

  async updateGroupMembers(groupId: number, userIds: number[]): Promise<void> {
    await this.apiService.put(`/groups/${groupId}/users/`, {
      users_ids: userIds
    });
  }

  async createGroup(name: string, description?: string) {
    try {
      interface GroupCreateRequest {
        name: string;
        description?: string;
      }
      // Construir o corpo da requisição com os parâmetros necessários
      const requestBody: GroupCreateRequest = {
        name
      };
      
      // Adicionar descrição apenas se for fornecida
      if (description !== undefined && description !== null) {
        requestBody.description = description;
      }
      
      const response = await this.apiService.post('/groups/', requestBody);

      console.log('Grupo criado com sucesso:', response.data);
      
      // Retornar os dados da resposta
      return response.data;
    } catch (error) {
      console.error('Erro API ao criar grupo:', error);
      throw error;
    }
  }

  async checkGroupNameExists(name: string): Promise<boolean> {
    try{
      const response = await this.apiService.get(`/groups/check-name/?name=${encodeURIComponent(name)}`)
      return response.data.exists
    }catch(error){
      console.error('Erro ao verificar o nome do grupo:', error);
      return false;
    }
  }
}