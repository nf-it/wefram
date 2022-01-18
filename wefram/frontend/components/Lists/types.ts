import React from 'react'
import {ApiEntityComplexResponse, ApiEntityResponse} from 'system/types'
import {RequestApiPath} from 'system/routing'


export type ListsSorting = {
  value: string
  direction: 'asc' | 'desc'
}

export type ListsSortingOption = {
  value: string
  caption: string
}

export type ListsSortingOptions = ListsSortingOption[]

export type ListsSelection = string[] | number[]

export type ListsProvidedFilters = Record<string, any>

export type FieldType =
  | 'string'
  | 'number'
  | 'boolean'
  | 'icon'
  | 'date'
  | 'dateTime'
  | 'dateNice'
  | 'dateTimeNice'

export type ListsFieldValueVizualizator = (value: any) => any

export type ListsFieldValueVisualize = Record<any, any> | ListsFieldValueVizualizator

export type ListsFieldStruct = {
  fieldType?: FieldType
  fieldName: string
  style?: object
  className?: string
  caption?: string | JSX.Element
  captionStyle?: object
  captionClassName?: string
  captionHint?: string
  textual?: boolean
  nullText?: string | boolean
  valueVisualize?: ListsFieldValueVisualize
  hidden?: boolean | ((value: any, field?: ListsFieldStruct) => boolean)
  render?: ((value: any, item?: any) => any) | null
  getter?: ((item: any) => any) | null  // used to return a value from the every item instead of item[fieldName]
}

export type ListsFieldType = string | ListsFieldStruct | null

export type ListsRowFields = ListsFieldType[]

export type ListsRowField = ListsFieldType | ListsFieldType[]

export type ListField = ListsFieldType | ListsRowFields | ListsRowField[] | null

export type UrlStateStorage = {
  sort?: string
  offset?: string
  limit?: string
  filters?: Record<string, string>
}

type ItemRouteCallback = (item: any) => string

type ProvListCommonProps = {
  /**
   * @typedef {Object} ProvListCommonProps - the common set of props for lists
   *
   * @property onAfterFetch - Called after fetch done and right before rendering items to make ability to make some changes,
   * or make some work on the higher level component using fetched items. The function must return the array of items whose
   * about to be rendered.
   *
   * @property selectable - If set to `true` - all items will be selectable; if set to `false` - none of items will be selectable
   * at all; if set to the array - only items with keys from the given array will be selectable, which gives
   * the higher component an ability to control whose items must be selectable and whose must not.
   */

  onAfterFetch?: (items: any[]) => any[]
  onError?: (err: any) => void
  onErrorShowMsg?: boolean | string
  onFetch?: (response: ApiEntityResponse | ApiEntityComplexResponse) => void
  onFetchDone?: (success?: boolean) => void
  onItemClick?: (item: any) => void
  onProvidedFiltersUpdateReq?: (filters: Record<string, any>) => void
  onSelection?: (items: ListsSelection) => void
  onPageChange?: (page: number, fetchCallback: any) => void
  onSortChange?: (sort: ListsSorting | null, fetchCallback: any) => void

  avatarColor?: string | boolean | ((item: any) => string | undefined)
  avatarFallback?: string | ((item: any) => JSX.Element | JSX.Element[] | null)
  avatarField?: string
  entityCaption?: string
  defaultSort?: ListsSorting
  emptyListText?: boolean | string
  providedFilters?: ListsProvidedFilters
  filtersEmptyAllowed?: string[]
  forbidUrlStateUpdate?: boolean
  itemComponent?: React.ElementType
  itemKeyField?: string
  itemsRoute?: string | ItemRouteCallback
  pagination?: boolean
  requestPath: RequestApiPath | string
  selectable?: boolean | any[]
  separated?: boolean
  sortOptions?: ListsSortingOptions
  storageEntity?: string
  textTotalCount?: string | boolean
  textTotalCountAll?: string | boolean
  unsortedOption?: boolean | string
  urlStateStorage?: UrlStateStorage

  items?: any[]
  itemsCount?: number
  itemsCountAll?: number

  selected?: ListsSelection
  sort?: ListsSorting | null

  offset?: number
  limit?: number
}

export type ProvListProps = ProvListCommonProps & {
  cardsOnRow?: number
  cardsOnRowCompactScreen?: number
  cardsOnRowWideScreen?: number
  primaryField?: ListField
  renderItemActions?: (item: any, index?: number, arr?: any[]) => JSX.Element | JSX.Element[] | null
  renderItemCardHeaderActions?: (item: any, index?: number, arr?: any[]) => JSX.Element | JSX.Element[] | null
  renderPrimaryField?: (item: any, field?: ListField) => JSX.Element | JSX.Element[] | null
  renderSecondaryField?: (item: any, field?: ListField) => JSX.Element | JSX.Element[] | null
  secondaryField?: ListField
  variant?: 'list' | 'cards'
}

export type ProvListOverridedParams = {
  sort?: ListsSorting
  offset?: number
  limit?: number
}

export type ProvTableColumn = ListsFieldStruct & {
  fieldAlign?: 'inherit' | 'left' | 'center' | 'right' | 'justify';
}

export type ProvTableColumns = ProvTableColumn[]

export type ProvTableProps = ProvListCommonProps & {
  columns: ProvTableColumns
  renderRowPrefix?: (item: any, index?: number, arr?: any[]) => JSX.Element | JSX.Element[] | null
  renderRowSuffix?: (item: any, index?: number, arr?: any[]) => JSX.Element | JSX.Element[] | null
  renderRowExpandedChild?: (item: any) => JSX.Element | JSX.Element[] | null
}

export type ProvTableOverridedParams = {
  sort?: ListsSorting
  offset?: number
  limit?: number
}
