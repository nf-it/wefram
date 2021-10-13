import {AxiosInstance} from 'axios'
import {aaa} from './aaa'

const axios = require('axios')


export function updateAuthorizationHeader(authorization: string | null): void {
  if (request.defaults.headers === undefined) {
    request.defaults.headers = {}
  }
  if (authorization) {
    request.defaults.headers['Authorization'] = authorization
  } else {
    delete request.defaults.headers['Authorization']
  }
}


export const request: AxiosInstance = axios.create()
request.defaults.headers = {}

updateAuthorizationHeader(aaa.getAuthorizationToken())
