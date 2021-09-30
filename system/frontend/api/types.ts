import {AxiosRequestConfig} from 'axios'
import {RequestApiPath, RequestPathParams} from 'system/routing'
import {CommonKey, EntityKey, TApiSubmitMethod} from 'system/types'


export interface IApiRequestConfig extends AxiosRequestConfig { }


export type API = {
  path(app: string, path: string, version?: number): RequestApiPath
  entityPath(appName: string, entityName: string, version?: number): RequestApiPath
  entityObjectPath(appName: string, entityName: string, version?: number): RequestApiPath
  pathToUrl(path: RequestApiPath): string
  pathWithParams(path: RequestApiPath, params: RequestPathParams): string
  get(path: RequestApiPath, config?: IApiRequestConfig): Promise<any>
  post(path: RequestApiPath, data?: any, config?: IApiRequestConfig): Promise<any>
  put(path: RequestApiPath, data?: any, config?: IApiRequestConfig): Promise<any>
  submit(method: TApiSubmitMethod, path: RequestApiPath, data?: any, config?: IApiRequestConfig): Promise<any>
  patch(path: RequestApiPath, data?: any, config?: IApiRequestConfig): Promise<any>
  delete(path: RequestApiPath, config?: IApiRequestConfig): Promise<any>
  deleteObject(path: RequestApiPath, key: EntityKey): Promise<any>
  deleteObjects(path: RequestApiPath, keys: string[] | number[]): Promise<any>
  head(path: RequestApiPath, config?: IApiRequestConfig): Promise<any>
  options(path: RequestApiPath, config?: IApiRequestConfig): Promise<any>
}


export type EntityOptionsResponse = Record<CommonKey, string>
export type EntityOptionsParams = {
  version?: number
  keys?: CommonKey[]
  like?: string
  ilike?: string
}
export type EntityCreateData = any
export type EntityCreateParams = {
  version?: number
}
export type EntityListParams = {
  version?: number
  filters?: Record<string, any>
  count?: boolean
  offset?: number
  limit?: number
  order?: string | string[]
  deep?: boolean
  like?: string
  ilike?: string
}
export type EntityListResponseList = any[]
export type EntityListResponseListCounted = {
  items: any[]
  itemsCount: number
}
export type EntityListResponse = EntityListResponseList | EntityListResponseListCounted
export type EntityGetParams = {
  version?: number
  deep?: boolean
}
export type EntityGetResponse = any
export type EntityUpdateParams = {
  version?: number
}
export type EntityUpdateData = any
export type EntitySubmitData = EntityCreateData | EntityUpdateData
export type EntitySubmitParams = EntityCreateParams & EntityUpdateParams
export type EntityDeleteParams = {
  version?: number
  keys?: CommonKey[]
}

export type EntityAPI = {
  options(appName: string, entityName: string, params?: EntityOptionsParams): Promise<EntityOptionsResponse>
  create(appName: string, entityName: string, data: EntityCreateData, params?: EntityCreateParams): Promise<CommonKey | string | boolean>
  list(appName: string, entityName: string, params?: EntityListParams): Promise<EntityListResponse>
  get(appName: string, entityName: string, key: CommonKey, params?: EntityGetParams): Promise<EntityGetResponse>
  update(appName: string, entityName: string, key: CommonKey, data: EntityUpdateData, params?: EntityUpdateParams): Promise<string | boolean>
  submit(appName: string, entityName: string, key: CommonKey | null, data: EntitySubmitData, params?: EntitySubmitParams): Promise<CommonKey | string | boolean>
  delete(appName: string, entityName: string, key: CommonKey | CommonKey[], params?: EntityDeleteParams): Promise<string | boolean>
}

