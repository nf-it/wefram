import {responses} from 'system/response'
import {gettext} from '../l10n'
import {NotificationInterface} from './types'
import {notificationsStore} from './mobx-store'



export const notifications: NotificationInterface = {
  showInfo(msg) {
    notificationsStore.message = msg
    notificationsStore.variant = 'info'
    notificationsStore.open = true
  },

  showSuccess(msg?) {
    notificationsStore.message = msg ?? gettext("Success")
    notificationsStore.variant = 'success'
    notificationsStore.open = true
  },

  showWarning(msg) {
    notificationsStore.message = msg
    notificationsStore.variant = 'warning'
    notificationsStore.open = true
  },

  showError(msg) {
    notificationsStore.message = msg
    notificationsStore.variant = 'error'
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
    notificationsStore.variant = 'error'
    notificationsStore.open = true
  },

  hide() {
    notificationsStore.open = false
  }
}

