import {runInAction} from 'mobx'
import {AaaSession, localStorageAuthorizationKeyname, AaaAuthorizationSession, ClientSessionResponse} from "./types";
import {aaaProvider} from "./provider";
import {session} from './session'
import {updateAuthorizationHeader} from 'system/requests'
import {AaaInterface} from './types'


export const aaa: AaaInterface = {
  async initializeFromServer() {
    await aaaProvider.touch().then(res => {
      const authsession: ClientSessionResponse = res.data
      aaa.initializeFromStruct(authsession)
    }).catch(() => {
      aaa.dropSession()
    })
  },

  initializeFromStruct(authsession: ClientSessionResponse) {
    runInAction(() => {
      session.user = authsession?.user || null
      session.permissions = authsession?.permissions || []
      if (authsession === null || authsession?.user === null) {
        aaa.dropAuthorizationSession()
      }
    })
  },

  dropSession() {
    runInAction(() => {
      session.user = null
      session.permissions = []
      aaa.dropAuthorizationSession()
    })
  },

  getAuthorizationSession(): AaaSession {
    const storedSession: string | null = localStorage.getItem(localStorageAuthorizationKeyname)
    if (storedSession === null)
      return null
    return JSON.parse(storedSession)
  },

  storeAuthorizationSession(session: AaaSession): void {
    localStorage.setItem(localStorageAuthorizationKeyname, JSON.stringify(session))
  },

  dropAuthorizationSession(): void {
    localStorage.removeItem(localStorageAuthorizationKeyname)
  },

  getAuthorizationToken(): string | null {
    const session: AaaSession = aaa.getAuthorizationSession()
    if (session === null)
      return null
    const token: string = String(session.token)
    return `Bearer ${token}`
  },

  getRefreshToken(): string | null {
    const session: AaaSession = aaa.getAuthorizationSession()
    if (session === null)
      return null
    return String(session.refreshToken)
  },

  async authenticate(username: string, password: string): Promise<AaaSession> {
    return await aaaProvider.login(username, password).then(response => {
      const authorizationSession: AaaAuthorizationSession = response.data
      aaa.storeAuthorizationSession(authorizationSession)
      updateAuthorizationHeader(aaa.getAuthorizationToken())
      return authorizationSession
    })
  },

  logout() {
    runInAction(() => {
      aaa.dropAuthorizationSession()
      session.user = null
      session.permissions = []
      updateAuthorizationHeader(null)
    })
  },

  isLoggedIn() {
    return session.user !== null
  },

  check() {
    return aaaProvider.check()
  }
}
