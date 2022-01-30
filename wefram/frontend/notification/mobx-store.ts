import {makeObservable, observable} from 'mobx'
import {NotificationVariant} from 'system/components'


/**
 * The MobX storage type for the notifications global state.
 */
class Store {

  /** Set to ``true`` to make the notification open. */
  open: boolean = false
  /** The notification message text. */
  message: string = ''
  /** The notification variant of the {NotificationVariant} */
  variant: NotificationVariant = 'info'

  constructor() {
    makeObservable(this, {
      open: observable,
      message: observable,
      variant: observable
    })
  }
}


/**
 * The MobX store for the notification global state.
 */
export const notificationsStore = new Store()
