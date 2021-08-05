import {Response} from './response'
import {IAppInstantiation} from './types'
import {api} from './api'
import {RequestApiPath} from './routing'


const instantiatePath: RequestApiPath = api.path('system', 'instantiate')


export type ProjectAppProvider = {
  instantiate(): Response<IAppInstantiation>
}

export const projectAppProvider: ProjectAppProvider = {
  instantiate(): Response<IAppInstantiation> {
    return api.get(instantiatePath)
  }
}
