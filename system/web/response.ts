export type BaseResponse<T> = {
  status: number,
  data: T
}

export type Response<T> = Promise<BaseResponse<T>>
