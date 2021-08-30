import {ISitemap} from './sitemap'
import {ISession} from 'system/aaa'
import {TLocaleDicrionary, Locale} from 'system/l10n'
import {IScreenRuntimes} from 'system/types/screens'


export interface IAaaConfiguration {
  rememberUsername: boolean
}

export interface IUrlConfiguration {
  loginScreenUrl: string
  defaultAuthenticatedUrl: string
  defaultGuestUrl: string
}

export interface IAppInstantiation {
  session: ISession
  sitemap: ISitemap
  screens: IScreenRuntimes
  locale: Locale
  title: string
  localization: TLocaleDicrionary
  urlConfiguration: IUrlConfiguration
  aaaConfiguration: IAaaConfiguration
}

