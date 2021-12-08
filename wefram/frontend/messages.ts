import React from 'react'
import {makeObservable, observable, runInAction} from 'mobx'
import {v4 as uuidv4} from 'uuid'


export type MessageAction = {
  caption: string
  highlight?: boolean
  onClick: (message: Message) => void
}

export type Message = {
  id?: string
  action?: (message: StoredMessage) => void
  actions?: MessageAction[]
  className?: string
  icon?: string
  timestamp?: string | null
  title?: string
  text: string
  tag?: string
}

export type StoredMessage = Message & {
  id: string
}

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

type MessagesInterface = {
  append(message: Message): string
  close(messageId: string): void
  closeAll(): void
  closeByClassName(className: string): void
  getMessage(id: string): StoredMessage | null
  getMessages(): StoredMessage[]
  hasMessages(): boolean
  hideBackdrop(): void
  openBackdrop(): void
}

export const messages: MessagesInterface = {
  append(message) {
    const id: string = uuidv4()
    const msg: StoredMessage = Object.assign({
      id: message.id ?? id,
      timestamp: message.timestamp ?? (new Date().toISOString())
    }, message)
    runInAction(() => {
      messagesStore.messages.push(msg)
      messagesStore.open = true
    })
    return id
  },

  close(messageId) {
    runInAction(() => {
      messagesStore.messages = messagesStore.messages.filter((msg: StoredMessage) => msg.id !== messageId)
      messagesStore.open = messagesStore.messages.length > 0
    })
  },

  closeAll() {
    runInAction(() => {
      messagesStore.messages = []
      messagesStore.open = false
    })
  },

  closeByClassName(className) {
    runInAction(() => {
      messagesStore.messages = messagesStore.messages.filter((msg: StoredMessage) => msg.className === className)
      messagesStore.open = messagesStore.messages.length > 0
    })
  },

  getMessage(id: string): StoredMessage | null {
    for (let i = 0; i < messagesStore.messages.length; i++) {
      if (messagesStore.messages[i].id === id)
        return messagesStore.messages[i]
    }
    return null
  },

  getMessages(): StoredMessage[] {
    return messagesStore.messages
  },

  hasMessages(): boolean {
    return messagesStore.messages.length > 0
  },

  hideBackdrop() {
    runInAction(() => {
      messagesStore.open = false
    })
  },

  openBackdrop() {
    runInAction(() => messagesStore.open = true)
  }
}


export type IMessages = {
  messages: StoredMessage[]
  open: boolean
}
