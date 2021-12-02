import {CommonKey} from 'system/types/common'

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

export type UserEditModel = {
  id: string | null
  login: string
  secret: string | null
  locked: boolean
  createdAt: null | string
  lastLogin: null | string
  firstName: string
  middleName: string
  lastName: string
  timezone: string | null
  locale: string | null
  comments: string
  fullName: string
  avatar: string | null
}

export type RoleEditModel = {
  id: string | null
  name: string
  permissions: string[]
  users: CommonKey[]
}

export type ActiveDirectoryDomainModel = {
  id: string | null
  enabled: boolean
  sort: number
  name: string
  domain: string
  server: string
}
