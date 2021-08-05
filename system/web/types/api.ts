import {CommonKey} from './common'

export type TApiSubmitMethod = 'PUT' | 'POST'
export type EntityKey = CommonKey
export type EntityCaption = string
export type EntityKeyCaption = Record<EntityKey, EntityCaption>
