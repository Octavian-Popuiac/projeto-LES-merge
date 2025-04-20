import { APIUserRepository } from '~/repositories/user/apiUserRepository'
import { UserItem } from '~/domain/models/user/user'

type UserCreateFields = {
  username: string
  first_name: string
  last_name: string
  password1: string
  password2: string
  email: string
}

export class UserApplicationService {
  constructor(private readonly repository: APIUserRepository) {}

  public async list(query: string): Promise<UserItem[]> {
    try {
      return await this.repository.list(query)
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'Erro ao listar utilizadores.')
    }
  }

  public async listAll(): Promise<UserItem[]> {
    try {
      return await this.repository.list2()
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'Erro ao listar todos os utilizadores.')
    }
  }

  public async getProfile(): Promise<UserItem> {
    try {
      return await this.repository.getProfile()
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'Erro ao obter o perfil.')
    }
  }

  public async create({
    username,
    first_name,
    last_name,
    password1,
    password2,
    email,
  }: UserCreateFields): Promise<void> {
    const payload = {
      username,
      first_name,
      last_name,
      password1,
      password2,
      email,
    }

    try {
      await this.repository.createRaw(payload)
    } catch (e: any) {
      console.error('Erro na criação (service):', e.response?.data)
      // Em vez de lançar erro genérico, relançamos o erro original
      throw e
    }
  }

  public async delete(user: UserItem): Promise<void> {
    try {
      await this.repository.delete(user.id)
    } catch (e: any) {
      throw new Error(e.response.data.detail)
    }
  }

  public async bulkDelete(users: UserItem[]): Promise<void> {
    const ids = users.map((user) => user.id)
    await this.repository.bulkDelete(ids)

  }



}
