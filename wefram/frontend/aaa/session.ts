import {observable, computed, makeObservable, toJS} from 'mobx'
import {SessionUser, Permissions} from '../types/aaa'


class Session {
  user: SessionUser | null = null
  permissions: Permissions = []

  constructor() {
    makeObservable(this, {
      user: observable,
      permissions: observable,
      displayName: computed,
      authenticated: computed
    })
  }

  get authenticated(): boolean {
    return toJS(this.user) !== null
  }

  get displayName(): string {
    const user = toJS(this.user)
    if (user === null)
      return ''
    return ([user.firstName, user.lastName].join(' ')).trim()
  }

  permitted = (requires: string | string[]): boolean => {
    if (!requires.length) {
      return true
    }
    if (!this.authenticated) {
      return false
    }
    if (this.permissions.length === 0) {
      return false
    }
    const scopes: Permissions = (!Array.isArray(requires)) ? [requires] : requires
    const permissions: Permissions = toJS(this.permissions)
    permissions.push('authenticated')
    for (let i = 0, l = scopes.length; i < l; i++) {
      if (permissions.includes(scopes[i]))
        continue
      return false
    }
    return true
  }
}

export interface ISession {
  user: SessionUser | null
  permissions: Permissions
}

export type ISessionResponse = ISession | null

export const session = new Session()
