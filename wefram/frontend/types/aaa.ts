import {EntityDateTime} from 'system/types/api'
import {CommonKey, UuidKey} from 'system/types/common'

export type AaaAuthorizationSession = {
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

export type AaaSessionUser = {
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

export type SessionUser = AaaSessionUser | null
export type Permissions = string[]

export type AaaSession = AaaAuthorizationSession | null

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
  roles: UuidKey[]
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

export type SessionLogModel = {
  id: number
  userId: UuidKey
  ts: EntityDateTime
  extra: any
}
