import {EntityAPI, IApiRequestConfig} from '../types'
import {api} from './api'
import {RequestApiPath} from 'system/routing'


export const entityApi: EntityAPI = {
  options(appName, entityName, params?) {
    const version: number | undefined = params?.version ?? undefined
    const path: RequestApiPath = api.entityPath(appName, entityName.concat(params?.keys ? '/resolve' : ''), version)
    const like: string | undefined = params?.like ?? undefined
    const ilike: string | undefined = params?.like ?? undefined
    const config: IApiRequestConfig = {
      params: { like, ilike }
    }

    if (params?.keys) {
      config.params.keys = params.keys
      return api.post(path, null, config).then(res => {
        return res.data
      })
    } else {
      return api.options(path, config).then(res => {
        return res.data
      })
    }
  },

  create(appName, entityName, data, params?) {
    const version: number | undefined = params?.version ?? undefined
    const path: RequestApiPath = api.entityPath(appName, entityName, version)
    return api.post(path, data).then(res => {
      return res.data ? res.data : true
    })
  },

  list(appName, entityName, params?) {
    const version: number | undefined = params?.version ?? undefined
    const path: RequestApiPath = api.entityPath(appName, entityName, version)
    const count: boolean | undefined = params?.count ?? undefined
    const offset: number | undefined = params?.offset ?? undefined
    const limit: number | undefined = params?.limit ?? undefined
    const order: string | string[] | undefined = params?.order ?? undefined
    const deep: boolean | undefined = params?.deep ?? undefined
    const like: string | undefined = params?.like ?? undefined
    const ilike: string | undefined = params?.ilike ?? undefined
    const config: IApiRequestConfig = {
      params: {
        count,
        offset,
        limit,
        order,
        deep,
        like,
        ilike
      }
    }
    if (params?.filters) {
      for (let k in params.filters) {
        if (!params.filters.hasOwnProperty(k))
          continue
        config.params[k] = params?.filters[k]
      }
    }
    return api.get(path, config).then(res => {
      return res.data
    })
  },

  get(appName, entityName, key, params?) {
    const version: number | undefined = params?.version ?? undefined
    const deep: boolean | undefined = params?.deep ?? undefined
    const path: RequestApiPath = api.pathWithParams(api.entityObjectPath(appName, entityName, version), {key})
    const config: IApiRequestConfig = {
      params: { deep }
    }
    return api.get(path, config).then(res => {
      return res.data
    })
  },

  update(appName, entityName, key, data, params?) {
    const version: number | undefined = params?.version ?? undefined
    const path: RequestApiPath = api.pathWithParams(api.entityObjectPath(appName, entityName, version), {key})
    return api.put(path, data).then(res => {
      return res.data
    })
  },

  submit(appName, entityName, key, data, params?) {
    const version: number | undefined = params?.version ?? undefined
    let path: RequestApiPath
    if (key !== null) {
      path = api.pathWithParams(api.entityObjectPath(appName, entityName, version), {key})
      return api.put(path, data).then(res => {
        return res.data ? res.data : true
      })
    } else {
      path = api.entityPath(appName, entityName, version)
      return api.post(path, data).then(res => {
        return res.data ? res.data : true
      })
    }
  },

  delete(appName, entityName, key, params?) {
    const version: number | undefined = params?.version ?? undefined
    let path: RequestApiPath
    const config: IApiRequestConfig = { }
    if (Array.isArray(key)) {
      config.params = { key }
      path = api.entityPath(appName, entityName, version)
    } else {
      path = api.pathWithParams(api.entityObjectPath(appName, entityName, version), {key})
    }
    return api.delete(path, config).then(res => {
      return res.data ? res.data : true
    })
  }
}
