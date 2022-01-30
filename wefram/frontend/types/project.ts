import {SidebarConfiguration} from './sidebar'
import {ClientSession} from 'system/aaa'
import {LocaleDicrionary, Locale} from 'system/l10n'
import {ScreensConfiguration} from 'system/types/screens'


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

