import { GroupItem, GroupItemList } from "./groups";
import { Permission } from "../permissions/permissions";
import { User } from "../metrics/metrics";

export interface GroupRepository {
  getGroups(): Promise<GroupItemList>;
  getGroup(id: number): Promise<GroupItem>;
  createGroup(name: string, description?: string): Promise<GroupItem>;
  updateGroup(id: number, data: {name: string, description?: string}): Promise<any>;
  deleteGroup(id: number): Promise<void>;
  addUsersToGroup(groupId: number, userIds: number[]): Promise<void>;
  removeUserFromGroup(groupId: number, userId: number): Promise<void>;
  getAllPermissions(): Promise<Permission[]>;
  getGroupPermissions(groupId: number): Promise<number[]>;
  updateGroupPermissions(groupId: number, permissionIds: number[]): Promise<void>;
  checkGroupNameExists(name: string): Promise<boolean>;
  getGroupMembers(id: number): Promise<User[]>;
  updateGroupMembers(id: number, members: number[]): Promise<void>;
}