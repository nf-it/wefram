export type IApiEntityResponse = any[]
export type IApiEntityComplexResponse = {
  items: IApiEntityResponse
  itemsCount: number
  itemsCountAll?: number
}

export type CommonKey = string | number
export type UuidKey = string
export type IntegerKey = number
