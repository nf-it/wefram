import {Response} from './response'
import {IProjectInstantiation} from './types'
import {api} from './api'
import {RequestApiPath} from './routing'


const instantiatePath: RequestApiPath = api.path('system', 'instantiate')


export type ProjectAppProvider = {
  instantiate(): Response<IProjectInstantiation>
}

export const projectProvider: ProjectAppProvider = {
  instantiate(): Response<IProjectInstantiation> {
    return api.get(instantiatePath)
  }
}
