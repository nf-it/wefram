import {Response} from 'system/response'
import {api} from 'system/api'
import {RequestApiPath} from 'system/routing'
import {ProjectAppProvider} from './types'


const instantiatePath: RequestApiPath = api.path('system', 'instantiate')
const managedScreenPrerenderPath: RequestApiPath = api.path('system', 'ui/screens/managed/on_render/{name}')


export const projectProvider: ProjectAppProvider = {
  instantiate() {
    return api.get(instantiatePath)
  },

  prerenderManagedScreen(name): Response<any> {
    return api.get(api.pathWithParams(managedScreenPrerenderPath, {
      name
    }))
  }
}
