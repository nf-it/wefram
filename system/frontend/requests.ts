import {AxiosInstance} from 'axios'
import {aaa} from './aaa'

const axios = require('axios')


export const request: AxiosInstance = axios.create()
request.defaults.headers.common['Authorization'] = aaa.getAuthorizationToken()
