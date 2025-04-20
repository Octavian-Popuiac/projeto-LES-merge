export interface GroupItem {
  id: number
  name: string
  description?: string
  created_by?: UserItem
  users?: UserItem[]
  members_count?: number
  permissions?: PermissionsItem[]
}

export type GroupItemList = GroupItem[]

export interface UserItem {
  id : number
  username: string
  email: string
}

export interface PermissionsItem {
  id: number
  name: string
  codename: string
  content_type: number
  description?: string
  category?: string
}