import React from 'react'
import {IApiEntityComplexResponse, IApiEntityResponse} from '../../types'
import {RequestApiPath} from '../../routing'


export type ListSorting = {
  value: string
  direction: 'asc' | 'desc'
}

export type ListSortingOption = {
  value: string
  caption: string
}

export type ListSortingOptions = ListSortingOption[]

export type ListSelection = string[] | number[]

export type ListProvidedFilters = Record<string, any>

export type FieldType = 'string' | 'number' | 'boolean' | 'icon' | 'date' | 'dateTime' | 'dateNice' | 'dateTimeNice'

export type ListFieldValueVizualizator = (value: any) => any

export type ListFieldValueVisualize = Record<any, any> | ListFieldValueVizualizator

export type ListFieldStruct = {
  fieldType?: FieldType
  fieldName: string
  style?: object
  className?: string
  caption?: string
  captionStyle?: object
  captionClassName?: string
  textual?: boolean
  nullText?: string | boolean
  valueVisualize?: ListFieldValueVisualize
}

export type ListFieldType = string | ListFieldStruct

export type ListRowFields = ListFieldType[]

export type ListRowField = ListFieldType | ListFieldType[]

export type ListField = ListFieldType | ListRowFields | ListRowField[]

export type UrlStateStorage = {
  sort?: string
  offset?: string
  limit?: string
  filters?: Record<string, string>
}

type ItemRouteCallback = (item: any) => string

export type ProvListProps = {
  entityCaption?: string
  onError?: (err: any) => void
  onErrorShowMsg?: boolean | string
  onFetch?: (response: IApiEntityResponse | IApiEntityComplexResponse) => void
  onFetchDone?: (success?: boolean) => void
  onItemClick?: (item: any) => void
  onProvidedFiltersUpdateReq?: (filters: Record<string, any>) => void
  onSelection?: (items: ListSelection) => void
  onPageChange?: (page: number, fetchCallback: any) => void
  onSortChange?: (sort: ListSorting | null, fetchCallback: any) => void

  avatarField?: string
  defaultSort?: ListSorting
  emptyListText?: boolean | string
  providedFilters?: ListProvidedFilters
  filtersEmptyAllowed?: string[]
  forbidUrlStateUpdate?: boolean
  itemAction?: (item: any) => void
  itemComponent?: React.ElementType
  itemKeyField?: string
  itemsRoute?: string | ItemRouteCallback
  pagination?: boolean
  primaryField?: string
  primaryComponent?: React.ElementType
  secondaryField?: ListField
  secondaryComponent?: React.ElementType
  requestPath: RequestApiPath | string
  selectable?: boolean
  separated?: boolean
  sortOptions?: ListSortingOptions
  textTotalCount?: string | boolean
  textTotalCountAll?: string | boolean
  unsortedOption?: boolean | string
  urlStateStorage?: UrlStateStorage

  items?: any[]
  itemsCount?: number
  itemsCountAll?: number

  selected?: ListSelection
  sort?: ListSorting | null

  offset?: number
  limit?: number
}

export type ProvListOverridedParams = {
  sort?: ListSorting
  offset?: number
  limit?: number
}
