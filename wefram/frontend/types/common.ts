export type ApiEntityResponse = any[]
export type ApiEntityComplexResponse = {
  items: ApiEntityResponse
  itemsCount: number
  itemsCountAll?: number
}

export type CommonKey = string | number
export type UuidKey = string
export type IntegerKey = number
