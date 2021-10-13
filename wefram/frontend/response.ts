import {runInAction} from 'mobx'
import {AxiosError, AxiosResponse} from 'axios'
import {gettext} from 'system/l10n'
import {routing} from 'system/routing'
import {aaa} from 'system/aaa'
import {runtime} from 'system/runtime'

export type AnyResponse = Promise<AxiosResponse<any>>

export type NoContentResponse = Promise<AxiosResponse<void>>

export type BaseResponse<T> = {
  status: number,
  data: T
}

export type Response<T> = Promise<BaseResponse<T>>

export type ResponsesRoutines = {
  handleCathedResponse(err: AxiosError): void
  responseSuccessMessage(res?: AxiosResponse): string
  responseErrorMessage(err?: AxiosError): string
}

export const responses: ResponsesRoutines = {
  handleCathedResponse(err) {
    const statusCode: number = err.response?.status || 500
    if (statusCode === 401) {
      aaa.isLoggedIn()
        ? (runInAction(() => runtime.reloginFormOpen = true))
        : routing.gotoLogin()
    }
  },

  responseSuccessMessage(res) {
    return res?.status === 204
      ? gettext("Succeed")
      : String(res?.data || gettext("Succeed"))
  },

  responseErrorMessage(err?) {
    const serverErrorMsg: string = gettext(
      "There is an error on the server, please try again a little later!"
    )
    const responseText: string =
      err?.response?.status === 500
      ? serverErrorMsg
      : String(err?.response?.data || serverErrorMsg)
    const statusCode: number = err?.response?.status || 400
    if (statusCode >= 500) {
      return serverErrorMsg
    } else if (statusCode === 400) {
      return gettext("Invalid request", 'system.responses')
    } else if (statusCode === 401) {
      return gettext("You must be signed in", 'system.responses')
    } else if (statusCode === 403) {
      return gettext("The access is denied", 'system.responses')
    } else {
      return responseText || gettext("Failed")
    }
  }
}
