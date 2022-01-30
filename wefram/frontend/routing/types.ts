
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


export type Routing = {
  requestPathToString(path: RequestPath): string
  assetPath(app: string, filename: string): string
  assetAbspath(filename: string): string
  screenPath(screenName: string): string | null
  gotoLogin(): void
  gotoDefault(): void
  gotoOnLogoff(): void
  gotoScreen(screenName: string): void
  gotoPath(path: string): void
  back(): void
  defaultPath(): string
}