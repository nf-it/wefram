import {makeObservable, observable} from 'mobx'
import {Location} from 'history'
import {Localization} from '@material-ui/core/locale'
import {IAppInstantiation, IScreenRuntimes, ISitemap} from './types'
import {projectAppProvider} from './provider'
import {aaa} from './aaa'
import {localization} from './l10n'


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
  rememberUsername: boolean = false
  sitemap: ISitemap = []
  screens: IScreenRuntimes = {}
  muiLocalization: Localization = {}

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
      muiLocalization: observable
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
    const scrollY: number = window.scrollY
    console.log('save scroll position', scrollID)
    this.scrollPositions[scrollID] = scrollY
  }

  restoreScrollPosition = (id?: string | Location) => {
    const scrollID: string = this.locationToString(id)
      ?? [window.location.pathname, window.location.search].join('')
    let scrollY: number | null = this.scrollPositions[scrollID]
    console.log('resore scroll position:', scrollID)
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
      runtime.loginScreenUrl = res.data.urlConfiguration.loginScreenUrl
      runtime.defaultAuthenticatedUrl = res.data.urlConfiguration.defaultAuthenticatedUrl
      runtime.defaultGuestUrl = res.data.urlConfiguration.defaultGuestUrl
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
