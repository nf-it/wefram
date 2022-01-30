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


export type MessagesMobxStoreType = {
  messages: StoredMessage[]
  open: boolean
}


export type MessagesInterface = {
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
