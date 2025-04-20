import ApiService from '@/services/api.service'
// import { Perspective, 
// PerspectiveQuestionBase, 
// PerspectiveQuestion, 
// PerspectiveMember 
// } from '~/domain/models/perspective/perspective'




export class APIPerspectiveRepository {
  constructor(private readonly request = ApiService) {}


  async getLabelPerspectives(projectId: number, exampleId: number): Promise<any> {
    const url = `/projects/${projectId}/examples/${exampleId}/labels-perspective/`
    const response = await this.request.get(url)
    return response.data
  }

}