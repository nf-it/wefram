import React from 'react'
import {ApiEntityComplexResponse, ApiEntityResponse} from 'system/types'
import {RequestApiPath} from 'system/routing'


export type EnumsSorting = {
  value: string
  direction: 'asc' | 'desc'
}


/**
 * The sorting option definition used in the enumerating component
 * */
export type EnumsSortingOption = {
  /** The actual field name (value) which to use in the API request. */
  value: string

  /** The human-readable caption which to render in the interface. This one may
   * be set using localization with `gettext()`. */
  caption: string
}


export type EnumsSortingOptions = EnumsSortingOption[]


export type EnumsSelection = string[] | number[]


export type EnumsProvidedFilters = Record<string, any>


/** The type of the field or table column. This affects on how the
 * corresponding value will be interpreted and shown to the user. */
export type FieldType =
  | 'string'          // Just a textual string (default)
  | 'number'          // The number
  | 'boolean'         // Yes or No (will be presented as Yes-No image)
  | 'icon'            // Icon (the value will be interpreted as src url)
  | 'date'            // Date in the strict form
  | 'dateTime'        // Date & time in the strict form
  | 'dateNice'        // The nice, textual format of the date
  | 'dateTimeNice'    // The nice, textual format of the date & time


/** Typedef for the callback which renders the field value instead
 * of the default behaviour. */
export type EnumsFieldValueVizualizator = (value: any) => any


export type EnumsFieldValueVisualize = Record<any, any> | EnumsFieldValueVizualizator


/**
 * The common field struct used when declaring columns and primary/secondary fields in the
 * enumerating components: ProvList & ProvTable.
 */
export type EnumsField = {

  /** The type of the field or table column. This affects on how the corresponding value will be
   * interpreted and shown to the user. */
  fieldType?: FieldType

  /** The name of the field, which must be the same as in the resulting data sent from backend to
   * the frontend (the same as entity field name). */
  fieldName: string

  /** The ability to override some styles on how the field about to be rendered. */
  style?: object

  /** The CSS class name(s) about to be applied to each rendering field. */
  className?: string

  /** The field caption (strongly recommends to fill up this property for the table variant of
   * enumerations). Might be a string or JSX element. */
  caption?: React.ReactNode

  /** The ability to override some caption styles (styles whose applies to the field caption, but
   * not to the field values). */
  captionStyle?: object

  /** The CSS class name(s) about to be applied to the field caption. */
  captionClassName?: string

  /** If set, the field caption will be followed with the hint icon and the user will get the hint
   * when moving mouse over the field caption hint. */
  captionHint?: string

  /** If set to ``true`` - the several field type-based variants, like ``boolean``, will be shown
   * to the user textual, avoiding using of icons, images or etc. */
  textual?: boolean

  /** Defines behaviour on when the field value is ``undefined`` or ``null``. If
   * not set - nothing will be rendered to the user (nothing shown). If set to the boolean ``true`` -
   * the textual dash (-) will be rendered. If set to some string value - this string value will be
   * shown to the user instead of null. */
  nullText?: string | boolean

  /** The dictionary describing values and accordning textual representations. This allows
   * to determine whether the raw value corresponds to the displayed textual value to the user.
   * As alternative to defining the static dict (Record key=>value) it is possible to assign the
   * callable callback here, which will get the value and return the rendering representation. */
  valueVisualize?: EnumsFieldValueVisualize

  /** If set to boolean ``true`` - the field will be hidden at all; if set to the callable
   * callback - then this callback will be called with the raw value and field definition
   * and expect the boolean result - do hide the field or do not. */
  hidden?: boolean | ((value: any, field?: EnumsField) => boolean)

  /** Optional callback which can be used to handle the value rendering. */
  render?: ((value: any, item?: any) => any) | null

  /** Optional callback which can be used to handle the raw value and return some computed value
   * instead. Useful when need to do some work with got values from the backend to make them
   * corretly or more understable readable by a user. If not set - by default the item's [fieldName]
   * value will be used (item[fieldName]). */
  getter?: ((item: any) => any) | null
}


export type EnumsFieldType = string | EnumsField | null


export type EnumsRowFields = EnumsFieldType[]


export type EnumsRowField = EnumsFieldType | EnumsFieldType[]


export type EnumField = EnumsFieldType | EnumsRowFields | EnumsRowField[] | null


/** The type used by ProvEnums to store state in the browser URL */
export type UrlStateStorage = {
  sort?: string
  offset?: string
  limit?: string
  filters?: Record<string, string>
}


/** The callback used as action for the item click */
type ItemRouteCallback = (item: any) => string


/** The common set of props for enumerating lists and tables */
type ProvEnumCommonProps = {

  /** Called after fetch done and right before rendering items to make ability to make some changes,
   * or make some work on the higher level component using fetched items. The function must return the array of items whose
   * about to be rendered. */
  onAfterFetch?: (items: any[]) => any[]

  onError?: (err: any) => void

  onErrorShowMsg?: boolean | string

  onFetch?: (response: ApiEntityResponse | ApiEntityComplexResponse) => void

  onFetchDone?: (success?: boolean) => void

  onItemClick?: (item: any) => void

  onProvidedFiltersUpdateReq?: (filters: Record<string, any>) => void

  /** The optional callback fired on every selection change - when user select an item, when user
   * deselect the item, and when user click on "Reverse selection" button. Useful for controlled selection. */
  onSelection?: (items: EnumsSelection) => void

  /** The optional callback fired when the user change the page (when pagination is enabled).
   * Useful for controlled pagination. */
  onPageChange?: (page: number, fetchCallback: any) => void

  /** The optional callback fired when sorting was changed by the user in the interface (if there are
   * sorting options and sorting options are enabled). Useful for controlled sorting. */
  onSortChange?: (sort: EnumsSorting | null, fetchCallback: any) => void

  /** The color of the avatar (if it is defined). Possible value types are
   * - `string` - the exact CSS color code, **or** the name of the field, which's value to use as color code;
   * - or `boolean` (set to `true` to automatically generate the avatar color basing on the item's alternative string).
   * - or `function` - the callback function `(item: any) => string | undefined` which get the item as argument and
   * about to return the CSS color code for the avatar. */
  avatarColor?: string | boolean | ((item: any) => string | undefined)

  /** Used to generate the fallback textual string if the avatar is defined, but there is
   * no avatar uploaded and nothing to show as the avatar image. */
  avatarFallback?: string | ((item: any) => React.ReactNode | null)

  /** The name of the corresponding item's field name to use as avatar image source. */
  avatarField?: string

  /** The optional caption used in the notifications and messages when something about
   * to be shown to the user with the entity name. Adviced to fill up this parameter, because otherwise the system
   * entity  name (the class name) will be used instead, which is not really understandable to the end user. */
  entityCaption?: string

  /** Optional default sorting option using type {EnumsSorting}. This sorting value will
   * be used both in the interface and within the API requests. */
  defaultSort?: EnumsSorting

  /** Optional parameter which defines the text which will be rendered to the end user
   * if there are no items fetched as the API request. Possible value types are `boolean` (if set to `true` -
   * display the default system text indicating that there are no items in the list) or `string`
   * (used to set the own text). */
  emptyListText?: boolean | string

  /** The dictionary consists of filters' names as keys and corresponding values;
   * these filters will be passed to the backend using standard API filtering mechanisms. Special case is
   * using `like` & `ilike` filter names - those names used to perform search operation (see backend
   * reference on `ds.model.Model.like()` & `ds.model.Model.ilike()` accordingly). */
  providedFilters?: EnumsProvidedFilters

  /** By default, if the any filter's value is the empty string - this filter
   * ignores and will not be included in the API request. This parameter is for avoiding of this behaviour
   * and passing empty string as the corresponding filter value (even if the value is empty, yes). This
   * parameter is a list of filters names for which this behaviour is applicable to. */
  filtersEmptyAllowed?: string[]

  /** The name of the key field of the item. By default, the name 'key' used as
   * the item key, and if there is no 'key' field - the 'id' name will be used. If the item has other
   * than one of those two names as a primary key - the name of this field must be set using this
   * parameter. */
  itemKeyField?: string

  /** If the item about to link to the any route and clicking on the item about to
   * switch to the specific URL - this parameter must be set to the corresponding route URL. In
   * addition, if the "{key}" is in the given URL - it will be replaced with the corresponding item
   * primary key value (see `itemKeyField` above). So, the good route looks like:
   *
   * `/myveryapp/myveryitem/{key}`
   *
   * As alternative, the callback, returning the per-item URL, might be assigned. */
  itemsRoute?: string | ItemRouteCallback

  /** If set to `true` - the pagination will be used to display enumeration;
   * the corresponding set of UI elements will be automatically rendered. Pagination uses API
   * request arguments `offset` and `limit` to control the offset (the start position from which
   * to select objects) and the quantity of fetching items. */
  pagination?: boolean

  /** REQUIRED! The path (URL) which to use in the API request. */
  requestPath: RequestApiPath | string

  /** If set to `true` - all items will be selectable; if set to `false` - none of items will be selectable
   * at all; if set to the array - only items with keys from the given array will be selectable, which gives
   * the higher component an ability to control whose items must be selectable and whose must not. */
  selectable?: boolean | any[]

  /** The array of sort options. If set, the selection of sorting will be
   * rendered to the end user, allowing to change the default sorting of items to another option. */
  sortOptions?: EnumsSortingOptions

  /** The name of the defined storage entity, used for the avatar
   * rendering. Used in combination with `avatarField` parameter. For example:
   * `myapp.myentity`. */
  storageEntity?: string

  /** If set to `true` - the total count of all items will be shown
   * (and the corresponding API request will be generated with total count request). If set
   * to {string} type - the given text will prepend the total count number instead of default
   * localized text. */
  textTotalCount?: string | boolean

  /** Allows to add the "Unsorted" option in the sorting options. By
   * default, if the sorting options are defined - the default sorting always used in the request
   * because the default sorting option is selected in the interface, even if the user don't
   * change anything. This property adds an "Unsorted" option at the top of all defined sorting
   * options and selecting this one will omit any sorting in the API request.
   * Possible values are `true` (enabled, add localized "Unsorted" option), `false` (default) -
   * do not add the "Unsorted" option, or {string} type - which enables this propery and overrides
   * the default localized name with the given one. */
  unsortedOption?: boolean | string

  /** Defines the behaviour on how the enumeration state stores in
   * the URL. If omitted (by default) - the current state will not being saved in the URL of the
   * current location. Otherwise, several or all state's arguments will be added to the currently
   * opened screen's URL. The state includes: `sort`, `offset`, `limit` & `filters`. The every
   * required to be saved to the URL state argument must be specified as {string} corresponding
   * name. */
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
  itemComponent?: React.ElementType
  primaryField?: EnumField
  renderItemActions?: (item: any, index?: number, arr?: any[]) => React.ReactNode | null
  renderItemCardHeaderActions?: (item: any, index?: number, arr?: any[]) => React.ReactNode | null
  renderPrimaryField?: (item: any, field?: EnumField) => React.ReactNode | null
  renderSecondaryField?: (item: any, field?: EnumField) => React.ReactNode | null
  secondaryField?: EnumField
  variant?: 'list' | 'cards'
}


export type ProvTableColumn = EnumsField & {
  fieldAlign?: 'inherit' | 'left' | 'center' | 'right' | 'justify';
}


export type ProvTableColumns = ProvTableColumn[]


export type ProvTableProps = ProvEnumCommonProps & {
  columns: ProvTableColumns
  renderRowPrefix?: (item: any, index?: number, arr?: any[]) => React.ReactNode | null
  renderRowSuffix?: (item: any, index?: number, arr?: any[]) => React.ReactNode | null
  renderRowExpandedChild?: (item: any) => React.ReactNode | null
}


export type ProvTableOverridedParams = {
  sort?: EnumsSorting
  offset?: number
  limit?: number
}
