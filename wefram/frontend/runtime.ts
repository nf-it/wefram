import {makeObservable, observable, runInAction} from 'mobx'
import {Location} from 'history'
import {Localization} from '@mui/material/locale'
import {IProjectInstantiation, IScreenRuntimes, ISitemap, Locale} from './types'
import {projectProvider} from './provider'
import {aaa} from './aaa'
import {localization, gettext} from './l10n'
import {notifications} from './notification'
import {routing} from './routing'


type ScrollPositions = Record<string, number>

class ProjectRuntime {
  production: boolean = true
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
      production: observable,
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

  public initialize = async (): Promise<IProjectInstantiation | null> => {
    return projectProvider.instantiate().then(res => {
      runInAction(() => {
        runtime.production = res.data.production
        runtime.title = res.data.title
        runtime.sitemap = res.data.sitemap
        runtime.screens = res.data.screens
        runtime.locale = res.data.locale
        runtime.loginScreenUrl = res.data.urlConfiguration.loginScreenUrl
        runtime.defaultAuthenticatedUrl = res.data.urlConfiguration.defaultAuthenticatedUrl
        runtime.defaultGuestUrl = res.data.urlConfiguration.defaultGuestUrl
        runtime.onLogoffUrl = res.data.urlConfiguration.onLogoffUrl
        runtime.rememberUsername = res.data.aaaConfiguration.rememberUsername
      })
      aaa.initializeFromStruct(res.data.session)
      localization.initializeFromStruct(res.data.localization)
      return res.data
    })
  }

  public logoff = (): void => {
    aaa.logout()
    runtime.initialize().then(() => {
      notifications.showSuccess(gettext("You have been logged out. Good bye.", 'system.aaa-messages'))
      routing.gotoOnLogoff()
    }).catch(err => {
      notifications.showRequestError(err)
      routing.gotoOnLogoff()
    })
  }

  private locationToString = (location?: string | Location, excludeSearch?: boolean): string | undefined => {
    if (location === undefined)
      return undefined
    if (typeof location == 'string')
      return location
    return excludeSearch ? location.pathname : [location.pathname, location.search].join('')
  }

  public saveScrollPosition = (id?: string | Location): void => {
    const scrollID: string = this.locationToString(id)
      ?? [window.location.pathname, window.location.search].join('')
    this.scrollPositions[scrollID] = window.scrollY
  }

  public restoreScrollPosition = (id?: string | Location): void => {
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

  public setBusy = (state?: boolean): void => {
    runInAction(() => runtime.busy = Boolean(state ?? true))
  }

  public dropBusy = (): void => {
    runtime.setBusy(false)
  }

}

export const runtime = new ProjectRuntime()

window.addEventListener('scroll', () => {
  runtime.saveScrollPosition()
})
