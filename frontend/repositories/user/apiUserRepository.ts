import { UserItem } from '@/domain/models/user/user'
import ApiService from '@/services/api.service'

function toModel(item: { [key: string]: any }): UserItem {
  return new UserItem(item.id,
    item.username,
    item.is_superuser,
    item.is_staff,
    item.email,
    item.date_joined
  )
}


export class APIUserRepository {
  constructor(private readonly request = ApiService) {}

  async getProfile(): Promise<UserItem> {
    const url = '/me'
    const response = await this.request.get(url)
    return toModel(response.data)
  }

  async list(query: string): Promise<UserItem[]> {
    const url = `/users?q=${query}`
    const response = await this.request.get(url)
    return response.data.map((item: { [key: string]: any }) => toModel(item))
  }

  async list2(): Promise<UserItem[]> {
    const url = `/users`
    const response = await this.request.get(url)
    return response.data.map((item: { [key: string]: any }) => toModel(item))
  }

  async createRaw(payload: {
    username: string
    first_name: string
    last_name: string
    password1: string
    password2: string
    email: string
  }): Promise<void> {
    const url = '/users/create'
    console.log(url, payload)
    await this.request.post(url, payload)
  }

  async delete(userId: number): Promise<void> {
    const url = `/users/${userId}/delete`
    await this.request.delete(url)
  }

  async bulkDelete(userIds: number[]): Promise<void> {
    const url = `/users/bulkdelete`
    await this.request.delete(url, { ids: userIds })
  }

}
