import {Response} from './response'
import {ProjectConfiguration} from './types'
import {api} from './api'
import {RequestApiPath} from './routing'


const instantiatePath: RequestApiPath = api.path('system', 'instantiate')


export type ProjectAppProvider = {
  instantiate(): Response<ProjectConfiguration>
}

export const projectProvider: ProjectAppProvider = {
  instantiate(): Response<ProjectConfiguration> {
    return api.get(instantiatePath)
  }
}
