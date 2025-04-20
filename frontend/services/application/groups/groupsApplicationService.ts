import { GroupRepository } from '~/domain/models/groups/groupRepository';
import { GroupItem, GroupItemList } from '~/domain/models/groups/groups';
import { User } from '~/domain/models/metrics/metrics';
import { Permission } from '~/domain/models/permissions/permissions';

export class GroupApplicationService {
  constructor(private readonly groupRepository: GroupRepository) {}

  public async getGroups(): Promise<GroupItemList> {
    return await this.groupRepository.getGroups();
  }

  public async getGroup(id: number): Promise<GroupItem> {
    return await this.groupRepository.getGroup(id);
  }

  public async getGroupMembers(id: number): Promise<User[]>{
    return await this.groupRepository.getGroupMembers(id);
  }

  public async createGroup(name: string, description?: string): Promise<GroupItem> {
    return await this.groupRepository.createGroup(name, description);
  }

  public async updateGroup(id: number, data: {name: string, description?: string}): Promise<any> {
    return await this.groupRepository.updateGroup(id, data);
  }

  public async updateGroupMembers(id: number, members: number[]): Promise<void> {
    await this.groupRepository.updateGroupMembers(id, members);
  }

  public async deleteGroup(id: number): Promise<void> {
    await this.groupRepository.deleteGroup(id);
  }

  public async addUsersToGroup(groupId: number, userIds: number[]): Promise<void> {
    await this.groupRepository.addUsersToGroup(groupId, userIds);
  }

  public async removeUserFromGroup(groupId: number, userId: number): Promise<void> {
    await this.groupRepository.removeUserFromGroup(groupId, userId);
  }

  public async getAllPermissions(): Promise<Permission[]> {
    return await this.groupRepository.getAllPermissions();
  }
  
  public async getGroupPermissions(groupId: number): Promise<number[]> {
    return await this.groupRepository.getGroupPermissions(groupId);
  }
  
  public async updateGroupPermissions(groupId: number, permissionIds: number[]): Promise<void> {
    await this.groupRepository.updateGroupPermissions(groupId, permissionIds);
  }

  public async checkGroupNameExists(name: string): Promise<boolean> {
    return await this.groupRepository.checkGroupNameExists(name);
  }
}