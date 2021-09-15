import {makeObservable, observable} from 'mobx'
import {Location} from 'history'
import {Localization} from '@material-ui/core/locale'
import {IAppInstantiation, IScreenRuntimes, ISitemap} from './types'
import {projectAppProvider} from './provider'
import {aaa} from './aaa'
import {localization, Locale} from './l10n'


export interface IRuntime {
  busy: boolean
}

type ScrollPositions = Record<string, number>

class _Runtime {
  busy: boolean = false
  title: string = '(devel)'
  loginScreenUrl: string = '/login'
  defaultGuestUrl: string = '/'
  defaultAuthenticatedUrl: string = '/'
  onLogoffUrl: string = '/'
  rememberUsername: boolean = false
  sitemap: ISitemap = []
  screens: IScreenRuntimes = {}
  locale: Locale = {
    name: 'en_US',
    weekStartsOn: 0,
    firstWeekContainsDate: 1,
    dateFormat: 'MM/dd/yyyy'
  }
  muiLocalization: Localization = {}
  reloginFormOpen: boolean = false

  scrollPositions: ScrollPositions = {}

  constructor() {
    makeObservable(this, {
      busy: observable,
      title: observable,
      loginScreenUrl: observable,
      defaultGuestUrl: observable,
      defaultAuthenticatedUrl: observable,
      rememberUsername: observable,
      sitemap: observable,
      muiLocalization: observable,
      reloginFormOpen: observable
    })
  }

  private locationToString = (location?: string | Location, excludeSearch?: boolean): string | undefined => {
    if (location === undefined)
      return undefined
    if (typeof location == 'string')
      return location
    return excludeSearch ? location.pathname : [location.pathname, location.search].join('')
  }

  saveScrollPosition = (id?: string | Location) => {
    const scrollID: string = this.locationToString(id)
      ?? [window.location.pathname, window.location.search].join('')
    this.scrollPositions[scrollID] = window.scrollY
  }

  restoreScrollPosition = (id?: string | Location) => {
    const scrollID: string = this.locationToString(id)
      ?? [window.location.pathname, window.location.search].join('')
    let scrollY: number | null = this.scrollPositions[scrollID]
    if (!scrollY)
      return
    window.scrollTo({
      top: scrollY,
      behavior: 'smooth'
    })
  }

}

export type AppInterface = {
  initializeApp(): Promise<IAppInstantiation | null>
}

export const appInterface: AppInterface = {
  async initializeApp(): Promise<IAppInstantiation | null> {
    return projectAppProvider.instantiate().then(res => {
      runtime.title = res.data.title
      runtime.sitemap = res.data.sitemap
      runtime.screens = res.data.screens
      runtime.locale = res.data.locale
      runtime.loginScreenUrl = res.data.urlConfiguration.loginScreenUrl
      runtime.defaultAuthenticatedUrl = res.data.urlConfiguration.defaultAuthenticatedUrl
      runtime.defaultGuestUrl = res.data.urlConfiguration.defaultGuestUrl
      runtime.onLogoffUrl = res.data.urlConfiguration.onLogoffUrl
      runtime.rememberUsername = res.data.aaaConfiguration.rememberUsername
      aaa.initializeFromStruct(res.data.session)
      localization.initializeFromStruct(res.data.localization)
      runtime.muiLocalization = localization.createMuiLocalization()
      return res.data
    })
  }
}


export const runtime = new _Runtime()


window.addEventListener('scroll', () => {
  runtime.saveScrollPosition()
})
