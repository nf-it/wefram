export interface IAuthorization {
  token: string
  refreshToken: string
  user: {
    id: string
    login: string
    firstName: string
    middleName: string
    fullName: string
    displayName: string
    lastName: string
    locale: string | null
    timezone: string | null
  }
  expire: string
  permissions: string[]
}

export interface ISessionUser {
  id: string
  login: string
  firstName: string
  middleName: string
  lastName: string
  fullName: string
  displayName: string
  locale: string | null
  timezone: string | null
}

export type SessionUser = ISessionUser | null
export type Permissions = string[]

export type IAuthorizationSession = IAuthorization | null

export const localStorageAuthorizationKeyname: string = 'system.aaa.authorization'
export const localStorageUsernameRememberKeyname: string = "system.aaa.rememberedUsername"
