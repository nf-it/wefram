import {createBrowserHistory} from 'history'
import {runtime} from 'system/project'
import {screensSchema} from 'build/screens'
import {session} from 'system/aaa'
import {Routing} from './types'


export const routingHistory = createBrowserHistory()

const STATIC_URL: string = '/static'


export const routing: Routing = {
  requestPathToString(path) {
    if (typeof path == 'string')
      return path
    return `/${[path.app.replace(/^\/+|\/+$/g, ''), path.path.replace(/^\/+|\/+$/g, '')].join('/')}`
  },

  assetPath(app, filename) {
    return `${STATIC_URL}/assets/${app}/${filename}`
  },

  assetAbspath(filename) {
    const prefix: string = `${STATIC_URL}/assets/`
    if (filename.startsWith(prefix))
      return filename
    return `${STATIC_URL}/assets/${filename.replace(/^\/+/g, '')}`
  },

  screenPath(screenName) {
    if (!(screenName in screensSchema))
      return null
    return screensSchema[screenName].routeUrl
  },

  gotoLogin() {
    routingHistory.push(runtime.loginScreenUrl)
  },

  gotoDefault() {
    routingHistory.push(routing.defaultPath())
  },

  gotoOnLogoff() {
    routingHistory.push(runtime.onLogoffUrl)
  },

  gotoScreen(screenName) {
    const routeUrl: string | null = routing.screenPath(screenName)
    if (routeUrl === null)
      return
    routingHistory.push(routeUrl)
  },

  gotoPath(path) {
    routingHistory.push(routing.requestPathToString(path))
  },

  back() {
    routingHistory.goBack()
  },

  defaultPath() {
    return session.authenticated
      ? runtime.defaultAuthenticatedUrl
      : runtime.defaultGuestUrl
  }
}
