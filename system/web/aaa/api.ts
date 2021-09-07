import {IAuthorizationSession, localStorageAuthorizationKeyname} from "../types/aaa";
import {aaaProvider} from "./provider";
import {IAuthorization} from "../types/aaa";
import {ISessionResponse, session} from './session'
import {request} from '../requests'


export type AaaInterface = {
  initializeFromServer(): Promise<any>
  initializeFromStruct(authsession: ISessionResponse): void
  dropSession(): void
  getAuthorizationSession(): IAuthorizationSession
  storeAuthorizationSession(session: IAuthorizationSession): void
  dropAuthorizationSession(): void
  getAuthorizationToken(): string | null
  getRefreshToken(): string | null
  authenticate(username: string, password: string): Promise<IAuthorizationSession>
  logout(): void
  isLoggedIn(): boolean
  check(): Promise<any>
}


export const aaa: AaaInterface = {
  async initializeFromServer() {
    await aaaProvider.touch().then(res => {
      const authsession: ISessionResponse = res.data
      aaa.initializeFromStruct(authsession)
    }).catch(() => {
      aaa.dropSession()
    })
  },

  initializeFromStruct(authsession: ISessionResponse) {
    session.user = authsession?.user || null
    session.permissions = authsession?.permissions || []
    if (authsession === null || authsession?.user === null) {
      aaa.dropAuthorizationSession()
    }
  },

  dropSession() {
    session.user = null
    session.permissions = []
    aaa.dropAuthorizationSession()
  },

  getAuthorizationSession(): IAuthorizationSession {
    const storedSession: string | null = localStorage.getItem(localStorageAuthorizationKeyname)
    if (storedSession === null)
      return null
    return JSON.parse(storedSession)
  },

  storeAuthorizationSession(session: IAuthorizationSession): void {
    localStorage.setItem(localStorageAuthorizationKeyname, JSON.stringify(session))
  },

  dropAuthorizationSession(): void {
    localStorage.removeItem(localStorageAuthorizationKeyname)
  },

  getAuthorizationToken(): string | null {
    const session: IAuthorizationSession = aaa.getAuthorizationSession()
    if (session === null)
      return null
    const token: string = String(session.token)
    return `Bearer ${token}`
  },

  getRefreshToken(): string | null {
    const session: IAuthorizationSession = aaa.getAuthorizationSession()
    if (session === null)
      return null
    return String(session.refreshToken)
  },

  async authenticate(username: string, password: string): Promise<IAuthorizationSession> {
    return await aaaProvider.login(username, password).then(response => {
      const authorizationSession: IAuthorization = response.data
      aaa.storeAuthorizationSession(authorizationSession)
      request.defaults.headers.common['Authorization'] = aaa.getAuthorizationToken()
      return authorizationSession
    })
  },

  logout() {
    aaa.dropAuthorizationSession()
    session.user = null
    session.permissions = []
    request.defaults.headers.common['Authorization'] = null
  },

  isLoggedIn() {
    return session.user !== null
  },

  check() {
    return aaaProvider.check()
  }
}
