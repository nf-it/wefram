export type ApiEntityResponse = any[]
export type ApiEntityComplexResponse = {
  items: ApiEntityResponse
  itemsCount: number
  itemsCountAll?: number
}

export type CommonKey = string | number
export type UuidKey = string
export type IntegerKey = number

export type ApiSubmitMethod = 'PUT' | 'POST'
export type EntityKey = CommonKey
export type EntityCaption = string
export type EntityKeyCaption = Record<EntityKey, EntityCaption>

export type EntityDate = string
export type EntityTime = string
export type EntityDateTime = string
export type EntityFile = string | null
export type EntityImage = string | null
