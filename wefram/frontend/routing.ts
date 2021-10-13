import {createBrowserHistory} from 'history'
import {runtime} from './runtime'
import {screensSchema} from 'build/screens'
import {session} from './aaa'
import buildConfig from '/build.json'


export type RequestAppPath = {
  app: string
  path: string
}

export type RequestPath = string | RequestAppPath
export type RequestPathParams = Record<string, any>

export interface RequestApiAppPath extends RequestAppPath {
  version?: number
}
export type RequestApiPath = RequestApiAppPath | string

export type RequestMethod =
  | 'GET'
  | 'POST'
  | 'PUT'
  | 'DELETE'
  | 'PATCH'




export const routingHistory = createBrowserHistory()

type Routing = {
  requestPathToString(path: RequestPath): string
  mediaAssetPath(app: string, filename: string): string
  mediaAssetAbspath(filename: string): string
  screenPath(screenName: string): string | null
  gotoLogin(): void
  gotoDefault(): void
  gotoOnLogoff(): void
  gotoScreen(screenName: string): void
  gotoPath(path: string): void
  back(): void
  defaultPath(): string
}

export const routing: Routing = {
  requestPathToString(path) {
    if (typeof path == 'string')
      return path
    return `/${[path.app.replace(/^\/+|\/+$/g, ''), path.path.replace(/^\/+|\/+$/g, '')].join('/')}`
  },

  mediaAssetPath(app, filename) {
    return `${buildConfig.staticsUrl}/media/${app}/${filename}`
  },

  mediaAssetAbspath(filename) {
    const prefix: string = `${buildConfig.staticsUrl}/media/`
    if (filename.startsWith(prefix))
      return filename
    return `${buildConfig.staticsUrl}/media/${filename.replace(/^\/+/g, '')}`
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
