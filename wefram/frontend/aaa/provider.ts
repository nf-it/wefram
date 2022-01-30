import {UuidKey} from 'system/types'
import {AaaAuthorizationSession, ClientSession} from './types'
import {aaa} from './api'
import {api} from '../api'
import {RequestApiPath} from '../routing'
import {NoContentResponse, Response} from '../response'


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


export type AaaProvider = {
  /**
   * Authenticate the user and open new session for this client browser
   *
   * @param username - the user login
   * @param password - plain text password
   */
  login(username: string, password: string): Response<AaaAuthorizationSession>

  /**
   * Refresh JWT token using refresh token
   */
  refreshToken(): Response<AaaAuthorizationSession>

  /**
   * Touch the current user session (prolong activity time) preventing session from
   * being closed by expiration time.
   */
  touch(): Response<ClientSession>

  /**
   * Test is current session valid. This method not touches the session and not
   * prolonging the session time.
   */
  check(): Response<any>

  /**
   * Lock given users (by their id) preventing their from login
   *
   * @param ids - the array of User->id whose to lock
   */
  lockUsers(ids: UuidKey[]): Response<NoContentResponse>

  /**
   * Unlocking given users (by their id) allowing them to login.
   *
   * @param ids - the array of User->id whose to unlock
   */
  unlockUsers(ids: UuidKey[]): Response<NoContentResponse>

  /**
   * Log given users off (by their id).
   *
   * @param ids - the array of User->id whose to log off
   */
  logoffUsers(ids: UuidKey[]): Response<NoContentResponse>
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

  lockUsers(ids: UuidKey[]): Response<NoContentResponse> {
    return api.post({
      app: 'system',
      path: 'users/lock',
      version: APIVER
    }, {
      ids
    })
  },

  unlockUsers(ids: UuidKey[]): Response<NoContentResponse> {
    return api.post({
      app: 'system',
      path: 'users/unlock',
      version: APIVER
    }, {
      ids
    })
  },

  logoffUsers(ids: UuidKey[]): Response<NoContentResponse> {
    return api.post({
      app: 'system',
      path: 'users/logoff',
      version: APIVER
    }, {
      ids
    })
  }
}
