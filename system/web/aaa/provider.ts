import {IAuthorization} from '../types/aaa'
import {aaa} from './api'
import {ISession} from './session'
import {api} from '../api'
import {RequestApiPath} from '../routing'
import {Response} from '../response'


const APIVER: number = 1
const AUTHPATH: RequestApiPath = {
  app: 'system',
  path: 'authenticate',
  version: APIVER
}


export type AaaProvider = {
  login(username: string, password: string): Response<IAuthorization>
  refreshToken(): Response<IAuthorization>
  touch(): Response<ISession>
}

export const aaaProvider: AaaProvider = {
  login(username: string, password: string): Response<IAuthorization> {
    return api.post(AUTHPATH, {
      username,
      password
    })
  },

  refreshToken(): Response<IAuthorization> {
    return api.put(AUTHPATH,
    {
      token: aaa.getRefreshToken()
    })
  },

  touch(): Response<ISession> {
    return api.get(AUTHPATH)
  }
}

