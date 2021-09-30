import {AxiosError} from 'axios'
import {RequestApiPath} from 'system/routing'
import {request} from 'system/requests'
import {responses} from 'system/response'
import {API} from '../types'


function _formatURL(path: RequestApiPath): string {
  if (typeof path === 'string')
    return String(path)

  const _ver: string = path.version ? `v${String(path.version)}/` : ''
  const _path: string = path.path.replace(/^\/+/g, '')
  return `/api/${path.app}/${_ver}${_path}`.replace(/\/\//g, '/').replace(/\/$/, '')
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
    return request.get(url, config).catch((err: AxiosError) => {
      responses.handleCathedResponse(err)  // handle error with global logics
      throw err  // forwarding the error state futher
    })
  },

  post(path, data?, config?) {
    const url: string = _formatURL(path)
    return request.post(url, data, config).catch((err: AxiosError) => {
      responses.handleCathedResponse(err)  // handle error with global logics
      throw err  // forwarding the error state futher
    })
  },

  put(path, data?, config?) {
    const url: string = _formatURL(path)
    return request.put(url, data, config).catch((err: AxiosError) => {
      responses.handleCathedResponse(err)  // handle error with global logics
      throw err  // forwarding the error state futher
    })
  },

  submit(method, path, data?, config?) {
    const url: string = _formatURL(path)
    return method === 'POST'
      ? request.post(url, data, config).catch((err: AxiosError) => {
          responses.handleCathedResponse(err)  // handle error with global logics
          throw err  // forwarding the error state futher
        })
      : request.put(url, data, config).catch((err: AxiosError) => {
          responses.handleCathedResponse(err)  // handle error with global logics
          throw err  // forwarding the error state futher
        })
  },

  patch(path, data?, config?) {
    const url: string = _formatURL(path)
    return request.patch(url, data, config).catch((err: AxiosError) => {
      responses.handleCathedResponse(err)  // handle error with global logics
      throw err  // forwarding the error state futher
    })
  },

  delete(path, config?) {
    const url: string = _formatURL(path)
    return request.delete(url, config).catch((err: AxiosError) => {
      responses.handleCathedResponse(err)  // handle error with global logics
      throw err  // forwarding the error state futher
    })
  },

  deleteObject(path, key) {
    const url: string = api.pathWithParams(path, { key })
    return request.delete(url).catch((err: AxiosError) => {
      responses.handleCathedResponse(err)  // handle error with global logics
      throw err  // forwarding the error state futher
    })
  },

  deleteObjects(path, keys) {
    const url: string = _formatURL(path)
    return request.delete(url, {
      params: { keys }
    }).catch((err: AxiosError) => {
      responses.handleCathedResponse(err)  // handle error with global logics
      throw err  // forwarding the error state futher
    })
  },

  head(path, config?) {
    const url: string = _formatURL(path)
    return request.head(url, config).catch((err: AxiosError) => {
      responses.handleCathedResponse(err)  // handle error with global logics
      throw err  // forwarding the error state futher
    })
  },

  options(path, config?) {
    const url: string = _formatURL(path)
    return request.options(url, config).catch((err: AxiosError) => {
      responses.handleCathedResponse(err)  // handle error with global logics
      throw err  // forwarding the error state futher
    })
  }
}


