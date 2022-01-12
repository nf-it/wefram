import {CommonKey} from './common'

export type ApiSubmitMethod = 'PUT' | 'POST'
export type EntityKey = CommonKey
export type EntityCaption = string
export type EntityKeyCaption = Record<EntityKey, EntityCaption>

export type EntityDate = string
export type EntityTime = string
export type EntityDateTime = string
export type EntityFile = string | null
export type EntityImage = string | null
