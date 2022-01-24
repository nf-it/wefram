import {Response} from './response'
import {ProjectConfiguration} from './types'
import {api} from './api'
import {RequestApiPath} from './routing'


const instantiatePath: RequestApiPath = api.path('system', 'instantiate')
const managedScreenPrerenderPath: RequestApiPath = api.path('system', 'ui/screens/managed/on_render/{name}')


export type ProjectAppProvider = {
  /** Used to fetch the instantiation data, describing the frontend environment for the
   * current user, from the backend.
   */
  instantiate(): Response<ProjectConfiguration>

  /** Used to fetch prerender data from the backend prior the ManagedScreen render */
  prerenderManagedScreen(name: string): Response<any>
}

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
