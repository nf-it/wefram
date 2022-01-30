import {AxiosResponse, AxiosError} from 'axios'
import {NotificationVariant} from 'system/components'


/**
 * The notification MobX store exportable type.
 */
export type NotificationMobxStoreType = {
  open: boolean
  message: string
  variant: NotificationVariant
}


export type NotificationInterface = {
  showInfo(msg: string): void
  showSuccess(msg?: string): void
  showWarning(msg: string): void
  showError(msg: string): void
  showRequestSuccess(res?: AxiosResponse): void
  showRequestError(err?: AxiosError): void
  showSomeServerError(): void
  hide(): void
}

