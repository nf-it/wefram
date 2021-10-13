import {AxiosInstance} from 'axios'
import {aaa} from './aaa'

const axios = require('axios')


export function updateAuthorizationHeader(authorization: string | null): void {
  if (authorization) {
    request.defaults.headers.common['Authorization'] = authorization
  } else {
    delete request.defaults.headers.common['Authorization']
  }
}


export const request: AxiosInstance = axios.create()
updateAuthorizationHeader(aaa.getAuthorizationToken())
