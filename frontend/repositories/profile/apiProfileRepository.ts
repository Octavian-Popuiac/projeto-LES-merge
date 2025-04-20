import ApiService from '@/services/api.service'
import { Group, GroupPermission } from '@/domain/models/profile/group'

function toPermissionModel(item: any): GroupPermission {
  return new GroupPermission(
    item.id,
    item.name,
    item.codename,
    item.app_label,
    item.model,
    item.verbose
  )
}

function toGroupModel(item: any): Group {
  const permissions = (item.permissions || []).map(toPermissionModel)
  return new Group(item.id, item.name, permissions)
}

export class APIGroupRepository {
  constructor(private readonly request = ApiService) {}

  async list(): Promise<Group[]> {
    const url = '/groups'
    const response = await this.request.get(url)
    console.log(response)
    return response.data.results.map((item: any) => toGroupModel(item))
  }

  // Para endpoints futuros:
  async get(id: number): Promise<Group> {
    const url = `/groups/${id}`
    const response = await this.request.get(url)
    return toGroupModel(response.data)
  }

  async create(payload: { name: string; permission_ids: number[] }): Promise<void> {
    await this.request.post('/groups', payload)
  }

  async update(id: number, payload: { name: string; permission_ids: number[] }): Promise<void> {
    await this.request.put(`/groups/${id}`, payload)
  }

  async delete(id: number): Promise<void> {
    await this.request.delete(`/groups/${id}`)
  }

  async listWithPermissions(): Promise<{
    groups: Group[]
    permissions: GroupPermission[]
  }> {
    const url = '/groups/with-permissions'
    const response = await this.request.get(url)

    const groups = response.data.groups.map(toGroupModel)
    const permissions = response.data.permissions.map(toPermissionModel)

    return { groups, permissions }
  }
}
