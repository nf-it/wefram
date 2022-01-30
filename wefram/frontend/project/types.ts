import {SidebarConfiguration} from 'system/sidebar'
import {ClientSession} from 'system/aaa'
import {LocaleDicrionary, Locale} from 'system/l10n'
import {ScreensConfiguration} from 'system/screens'
import {Response} from 'system/response'


export type ProjectDevelopmentConfiguration = Record<string, any>


export type ProjectAaaConfiguration = {
  rememberUsername: boolean
}


export type ProjectUrlConfiguration = {
  loginScreenUrl: string
  defaultAuthenticatedUrl: string
  defaultGuestUrl: string
  onLogoffUrl: string
}


export type ProjectConfiguration = {
  production: boolean
  development: ProjectDevelopmentConfiguration
  session: ClientSession
  sidebar: SidebarConfiguration
  screens: ScreensConfiguration
  locale: Locale
  title: string
  localization: LocaleDicrionary
  urlConfiguration: ProjectUrlConfiguration
  aaaConfiguration: ProjectAaaConfiguration
}


export type ProjectAppProvider = {
  /** Used to fetch the instantiation data, describing the frontend environment for the
   * current user, from the backend.
   */
  instantiate(): Response<ProjectConfiguration>

  /** Used to fetch prerender data from the backend prior the ManagedScreen render */
  prerenderManagedScreen(name: string): Response<any>
}
