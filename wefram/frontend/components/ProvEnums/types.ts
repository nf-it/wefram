import React from 'react'
import {ApiEntityComplexResponse, ApiEntityResponse} from 'system/types'
import {RequestApiPath} from 'system/routing'


export type EnumsSorting = {
  value: string
  direction: 'asc' | 'desc'
}


export type EnumsSortingOption = {
  value: string
  caption: string
}


export type EnumsSortingOptions = EnumsSortingOption[]


export type EnumsSelection = string[] | number[]


export type EnumsProvidedFilters = Record<string, any>


export type FieldType =
  | 'string'          // Just a textual string (default)
  | 'number'          // The number
  | 'boolean'         // Yes or No (will be presented as Yes-No image)
  | 'icon'            // Icon (the value will be interpreted as src url)
  | 'date'            // Date in the strict form
  | 'dateTime'        // Date & time in the strict form
  | 'dateNice'        // The nice, textual format of the date
  | 'dateTimeNice'    // The nice, textual format of the date & time

export type EnumsFieldValueVizualizator = (value: any) => any


export type EnumsFieldValueVisualize = Record<any, any> | EnumsFieldValueVizualizator


export type EnumsFieldStruct = {
  /**
   * The common field struct used when declaring columns and primary/secondary fields
   * in the enumerating components: ProvList & ProvTable.
   *
   * @property fieldType - The type of the field or table column. This affects on how the
   * corresponding value will be interpreted and shown to the user.
   *
   * @property fieldName - The name of the field, which must be the same as in the resulting
   * data sent from backend to the frontend (the same as entity field name).
   *
   * @property style - The ability to override some styles on how the field about to be
   * rendered.
   *
   * @property className - The CSS class name(s) about to be applied to each rendering field.
   *
   * @property caption - The field caption (strongly recommends to fill up this property for
   * the table variant of enumerations). Might be a string or JSX element.
   *
   * @property captionStyle - The ability to override some caption styles (styles whose
   * applies to the field caption, but not to the field values).
   *
   * @property captionClassName - The CSS class name(s) about to be applied to the field caption.
   *
   * @property captionHint - If set, the field caption will be followed with the hint icon and
   * the user will get the hint when moving mouse over the field caption hint.
   *
   * @property textual - If set to ``true`` - the several field type-based variants, like ``boolean``,
   * will be shown to the user textual, avoiding using of icons, images or etc.
   *
   * @property nullText - Defines behaviour on when the field value is ``undefined`` or ``null``. If
   * not set - nothing will be rendered to the user (nothing shown). If set to the boolean ``true`` -
   * the textual dash (-) will be rendered. If set to some string value - this string value will be
   * shown to the user instead of null.
   *
   * @property valueVisualize - The dictionary describing values and accordning textual
   * representations. This allows to determine whether the raw value corresponds to the displayed
   * textual value to the user.
   * As alternative to defining the static dict (Record key=>value) it is possible to assign
   * the callable callback here, which will get the value and return the rendering representation.
   *
   * @property hidden - If set to boolean ``true`` - the field will be hidden at all; if set to the
   * callable callback - then this callback will be called with the raw value and field definition
   * and expect the boolean result - do hide the field or do not.
   *
   * @property render - Optional callback which can be used to handle the value rendering.
   *
   * @property getter - Optional callback which can be used to handle the raw value and return some
   * computed value instead. Useful when need to do some work with got values from the backend to
   * make them corretly or more understable readable by a user.
   */

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
  valueVisualize?: EnumsFieldValueVisualize
  hidden?: boolean | ((value: any, field?: EnumsFieldStruct) => boolean)
  render?: ((value: any, item?: any) => any) | null
  getter?: ((item: any) => any) | null  // used to return a value from the every item instead of item[fieldName]
}


export type EnumsFieldType = string | EnumsFieldStruct | null


export type EnumsRowFields = EnumsFieldType[]


export type EnumsRowField = EnumsFieldType | EnumsFieldType[]


export type EnumField = EnumsFieldType | EnumsRowFields | EnumsRowField[] | null


export type UrlStateStorage = {
  sort?: string
  offset?: string
  limit?: string
  filters?: Record<string, string>
}


type ItemRouteCallback = (item: any) => string


type ProvEnumCommonProps = {
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
  onSelection?: (items: EnumsSelection) => void
  onPageChange?: (page: number, fetchCallback: any) => void
  onSortChange?: (sort: EnumsSorting | null, fetchCallback: any) => void

  avatarColor?: string | boolean | ((item: any) => string | undefined)
  avatarFallback?: string | ((item: any) => JSX.Element | JSX.Element[] | null)
  avatarField?: string
  entityCaption?: string
  defaultSort?: EnumsSorting
  emptyListText?: boolean | string
  providedFilters?: EnumsProvidedFilters
  filtersEmptyAllowed?: string[]
  forbidUrlStateUpdate?: boolean
  itemComponent?: React.ElementType
  itemKeyField?: string
  itemsRoute?: string | ItemRouteCallback
  pagination?: boolean
  requestPath: RequestApiPath | string
  selectable?: boolean | any[]
  separated?: boolean
  sortOptions?: EnumsSortingOptions
  storageEntity?: string
  textTotalCount?: string | boolean
  textTotalCountAll?: string | boolean
  unsortedOption?: boolean | string
  urlStateStorage?: UrlStateStorage

  items?: any[]
  itemsCount?: number
  itemsCountAll?: number

  selected?: EnumsSelection
  sort?: EnumsSorting | null

  offset?: number
  limit?: number
}


export type ProvListOverridedParams = {
  sort?: EnumsSorting
  offset?: number
  limit?: number
}


export type ProvListProps = ProvEnumCommonProps & {
  cardsOnRow?: number
  cardsOnRowCompactScreen?: number
  cardsOnRowWideScreen?: number
  primaryField?: EnumField
  renderItemActions?: (item: any, index?: number, arr?: any[]) => JSX.Element | JSX.Element[] | null
  renderItemCardHeaderActions?: (item: any, index?: number, arr?: any[]) => JSX.Element | JSX.Element[] | null
  renderPrimaryField?: (item: any, field?: EnumField) => JSX.Element | JSX.Element[] | null
  renderSecondaryField?: (item: any, field?: EnumField) => JSX.Element | JSX.Element[] | null
  secondaryField?: EnumField
  variant?: 'list' | 'cards'
}


export type ProvTableColumn = EnumsFieldStruct & {
  fieldAlign?: 'inherit' | 'left' | 'center' | 'right' | 'justify';
}


export type ProvTableColumns = ProvTableColumn[]


export type ProvTableProps = ProvEnumCommonProps & {
  columns: ProvTableColumns
  renderRowPrefix?: (item: any, index?: number, arr?: any[]) => JSX.Element | JSX.Element[] | null
  renderRowSuffix?: (item: any, index?: number, arr?: any[]) => JSX.Element | JSX.Element[] | null
  renderRowExpandedChild?: (item: any) => JSX.Element | JSX.Element[] | null
}


export type ProvTableOverridedParams = {
  sort?: EnumsSorting
  offset?: number
  limit?: number
}
