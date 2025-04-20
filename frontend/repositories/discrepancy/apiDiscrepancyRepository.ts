import ApiService from '@/services/api.service'
import { Discrepancy } from '~/domain/models/discrepancy/discrepancy'

function toModel(item: any): Discrepancy {
  return new Discrepancy(
    item.id,
    item.project,
    item.example,
    item.labels,
    item.status,
    item.created_at
  )
}

export class APIDiscrepancyRepository {
  constructor(private readonly request = ApiService) {}

  async list(projectId: number): Promise<Discrepancy[]> {
    const url = `/projects/${projectId}/discrepancies?limit=50`
    const response = await this.request.get(url)
    console.log('🔍 response.data:', response.data)
    return response.data.results.map(toModel)
  }

  async detect(projectId: number): Promise<any> {
    const url = `/projects/${projectId}/discrepancies/detect`
    const response = await this.request.get(url)
    console.log(response.data)
    return response.data
  }

  async save(projectId: number, exampleId: number, labels: any[]): Promise<Discrepancy> {
    const url = `/projects/${projectId}/examples/${exampleId}/discrepancies/save`
    const payload = {
      project: projectId,
      example: exampleId,
      labels,
      status: 'unresolved'
    }
    const response = await this.request.post(url, payload)
    return toModel(response.data)
  }

  async updateStatus(discrepancyId: number, status: string): Promise<Discrepancy> {
    const url = `/discrepancies/${discrepancyId}/`
    const payload = { status }
    const response = await this.request.patch(url, payload)
    return toModel(response.data)
  }

  async delete(discrepancyId: number): Promise<void> {
    const url = `/discrepancies/${discrepancyId}/`
    await this.request.delete(url)
  }
}

