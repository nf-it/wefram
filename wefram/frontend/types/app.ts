import {ISitemap} from './sitemap'
import {ISession} from 'system/aaa'
import {LocaleDicrionary, Locale} from 'system/types'
import {IScreenRuntimes} from 'system/types/screens'


export interface IAaaConfiguration {
  rememberUsername: boolean
}

export interface IUrlConfiguration {
  loginScreenUrl: string
  defaultAuthenticatedUrl: string
  defaultGuestUrl: string
  onLogoffUrl: string
}

export interface IProjectInstantiation {
  production: boolean
  session: ISession
  sitemap: ISitemap
  screens: IScreenRuntimes
  locale: Locale
  title: string
  localization: LocaleDicrionary
  urlConfiguration: IUrlConfiguration
  aaaConfiguration: IAaaConfiguration
}

