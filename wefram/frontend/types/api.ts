import {CommonKey} from './common'

export type ApiSubmitMethod = 'PUT' | 'POST'
export type EntityKey = CommonKey
export type EntityCaption = string
export type EntityKeyCaption = Record<EntityKey, EntityCaption>
