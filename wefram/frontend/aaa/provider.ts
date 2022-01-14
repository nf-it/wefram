import {UuidKey} from 'system/types'
import {AaaAuthorizationSession, SessionLogModel} from '../types/aaa'
import {aaa} from './api'
import {ClientSession} from './session'
import {api} from '../api'
import {RequestApiPath} from '../routing'
import {Response} from '../response'


const APIVER: number = 1
const AUTHPATH: RequestApiPath = {
  app: 'system',
  path: 'authenticate',
  version: APIVER
}
const CHECKPATH: RequestApiPath = {
  app: 'system',
  path: 'check',
  version: APIVER
}
// const SESSIONLOGPATH: RequestApiPath = api.entityPath('system', 'SessionLog')


export type AaaProvider = {
  login(username: string, password: string): Response<AaaAuthorizationSession>
  refreshToken(): Response<AaaAuthorizationSession>
  touch(): Response<ClientSession>
  check(): Response<any>
  // getSessionLog(userId: UuidKey): Response<SessionLogModel[]>
}

export const aaaProvider: AaaProvider = {
  login(username, password) {
    return api.post(AUTHPATH, {
      username,
      password
    })
  },

  refreshToken() {
    return api.put(AUTHPATH,
    {
      token: aaa.getRefreshToken()
    })
  },

  touch() {
    return api.get(AUTHPATH)
  },

  check() {
    return api.get(CHECKPATH, {
      headers: {
        'X-Avoid-Session-Touch': 'true',
        'Authorization': aaa.getAuthorizationToken() ?? ''
      }
    })
  },

  // getSessionLog(userId) {
  //   return api.get(SESSIONLOGPATH, {
  //     params: {
  //       userId
  //     }
  //   })
  // }
}
