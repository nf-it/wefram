import {makeObservable, observable, runInAction} from 'mobx'
import {v4 as uuidv4} from 'uuid'
import {StoredMessage, MessagesInterface} from './types'
import {messagesStore} from './mobx-store'


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
