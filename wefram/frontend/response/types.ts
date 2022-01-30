import {AxiosError, AxiosResponse} from 'axios'


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

