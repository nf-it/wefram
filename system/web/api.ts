import {AxiosRequestConfig} from 'axios'
import {request} from './requests'
import {RequestApiPath, RequestPathParams} from './routing'
import {EntityKey, TApiSubmitMethod} from './types'


function _formatURL(path: RequestApiPath): string {
  if (typeof path === 'string')
    return String(path)

  const _ver: string = path.version ? `v${String(path.version)}/` : ''
  const _path: string = path.path.replace(/^\/+/g, '')
  return `/api/${path.app}/${_ver}${_path}`.replace(/\/\//g, '/').replace(/\/$/, '')
}


interface IApiRequestConfig extends AxiosRequestConfig { }


export type API = {
  path(
    app: string,
    path: string,
    version?: number
  ): RequestApiPath

  entityPath(
    appName: string,
    entityName: string,
    version?: number
  ): RequestApiPath

  entityObjectPath(
    appName: string,
    entityName: string,
    version?: number
  ): RequestApiPath

  pathToUrl(
    path: RequestApiPath
  ): string

  pathWithParams(
    path: RequestApiPath,
    params: RequestPathParams
  ): string

  get(
    path: RequestApiPath,
    config?: IApiRequestConfig
  ): Promise<any>

  post(
    path: RequestApiPath,
    data?: any,
    config?: IApiRequestConfig
  ): Promise<any>

  put(
    path: RequestApiPath,
    data?: any,
    config?: IApiRequestConfig
  ): Promise<any>

  submit(
    method: TApiSubmitMethod,
    path: RequestApiPath,
    data?: any,
    config?: IApiRequestConfig
  ): Promise<any>

  patch(
    path: RequestApiPath,
    data?: any,
    config?: IApiRequestConfig
  ): Promise<any>

  delete(
    path: RequestApiPath,
    config?: IApiRequestConfig
  ): Promise<any>

  deleteObject(
    path: RequestApiPath,
    key: EntityKey
  ): Promise<any>

  deleteObjects(
    path: RequestApiPath,
    keys: string[] | number[]
  ): Promise<any>

  head(
    path: RequestApiPath,
    config?: IApiRequestConfig
  ): Promise<any>

  options(
    path: RequestApiPath,
    config?: IApiRequestConfig
  ): Promise<any>
}

export const api: API = {
  path(app, path, version?) {
    const res: RequestApiPath = {
      app, path
    }
    if (version) {
      res.version = version
    }
    return res
  },

  entityPath(appName, entityName, version) {
    return {
      app: appName,
      path: entityName,
      version
    }
  },

  entityObjectPath(appName, entityName, version) {
    return {
      app: appName,
      path: `${entityName}/{key}`,
      version
    }
  },

  pathToUrl(path) {
    return _formatURL(path)
  },

  pathWithParams(path, params) {
    let result: string = _formatURL(path)
    let paramValue: any
    let re: RegExp
    for (let paramName in params) {
      if (!params.hasOwnProperty(paramName))
        continue
      paramValue = params[paramName] !== undefined ? params[paramName] : ''
      re = new RegExp(`{${paramName}}`, 'g')
      result = result.replace(re, paramValue !== undefined ? String(paramValue) : '')
    }
    return result.replace(/\/\//g, '/').replace(/\/$/, '')
  },

  get(path, config?) {
    const url: string = _formatURL(path)
    return request.get(url, config)
  },

  post(path, data?, config?) {
    const url: string = _formatURL(path)
    return request.post(url, data, config)
  },

  put(path, data?, config?) {
    const url: string = _formatURL(path)
    return request.put(url, data, config)
  },

  submit(method, path, data?, config?) {
    const url: string = _formatURL(path)
    return method === 'POST' ? request.post(url, data, config) : request.put(url, data, config)
  },

  patch(path, data?, config?) {
    const url: string = _formatURL(path)
    return request.patch(url, data, config)
  },

  delete(path, config?) {
    const url: string = _formatURL(path)
    return request.delete(url, config)
  },

  deleteObject(path, key) {
    const url: string = api.pathWithParams(path, { key })
    return request.delete(url)
  },

  deleteObjects(path, keys) {
    const url: string = _formatURL(path)
    return request.delete(url, {
      params: { keys }
    })
  },

  head(path, config?) {
    const url: string = _formatURL(path)
    return request.head(url, config)
  },

  options(path, config?) {
    const url: string = _formatURL(path)
    return request.options(url, config)
  }
}
