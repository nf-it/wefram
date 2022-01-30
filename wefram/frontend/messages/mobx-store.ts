import {makeObservable, observable, runInAction} from 'mobx'
import {v4 as uuidv4} from 'uuid'
import {StoredMessage} from './types'


class Store {
  messages: StoredMessage[] = []
  open: boolean = false

  constructor() {
    makeObservable(this, {
      messages: observable,
      open: observable
    })
  }
}

export const messagesStore = new Store()
