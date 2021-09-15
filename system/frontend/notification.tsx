import {makeObservable, observable} from 'mobx'
import {AxiosResponse, AxiosError} from 'axios'
import {VariantIcon} from './components'
import {responses} from 'system/response'
import {gettext} from './l10n'


class Store {
  open: boolean = false
  message: string = ''
  type: keyof VariantIcon = 'info'

  constructor() {
    makeObservable(this, {
      open: observable,
      message: observable,
      type: observable
    })
  }
}

export const notificationsStore = new Store()

type NotificationInterface = {
  showInfo(msg: string): void
  showSuccess(msg?: string): void
  showWarning(msg: string): void
  showError(msg: string): void
  showRequestSuccess(res?: AxiosResponse): void
  showRequestError(err?: AxiosError): void
  showSomeServerError(): void
  hide(): void
}

export const notifications: NotificationInterface = {
  showInfo(msg) {
    notificationsStore.message = msg
    notificationsStore.type = 'info'
    notificationsStore.open = true
  },

  showSuccess(msg?) {
    notificationsStore.message = msg ?? gettext("Success")
    notificationsStore.type = 'success'
    notificationsStore.open = true
  },

  showWarning(msg) {
    notificationsStore.message = msg
    notificationsStore.type = 'warning'
    notificationsStore.open = true
  },

  showError(msg) {
    notificationsStore.message = msg
    notificationsStore.type = 'error'
    notificationsStore.open = true
  },

  showRequestSuccess(res) {
    notifications.showSuccess(responses.responseSuccessMessage(res))
  },

  showRequestError(err) {
    notifications.showError(responses.responseErrorMessage(err))
  },

  showSomeServerError() {
    notificationsStore.message = gettext(
      "There is an error on the server, please try again a little later!"
    )
    notificationsStore.type = 'error'
    notificationsStore.open = true
  },

  hide() {
    notificationsStore.open = false
  }
}


export interface INotification {
  open: boolean
  message: string
  type: keyof VariantIcon
}

