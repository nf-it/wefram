import {EnumsSelection, ProvListProps, ProvTableProps} from 'system/components'
import {RequestApiPath} from 'system/routing'


export type EntityEnumsProps = {
  /**
   * @typedef {Object} EntityEnumsProps - The common props type for EntityList & EntityTable
   *
   * @property addButtonAction - Optional callback used as action on "Add" button click, if the
   * `addButtonPath` property is not set.
   *
   * @property addButtonCaption - Optional, the caption for the "Add" button; if omitted - the
   * default localized "Add" will be used.
   *
   * @property addScreenPath - Optional, the request path (URL) to the screen which renders
   * the "Add object" functionality for the entity.
   *
   * @property controls - Optional set of JSX element about to be rendered in the controls area,
   * next to the buttons like "Add", "Delete", and next to the search text input (if enabled). This
   * makes possible to extend the default controls layout, adding own elements, like extra buttons,
   * text labels, etc.
   *
   * @property deleteButtonCaption - Optional, the caption for the "Delete" button; if omitted -
   * the default localized "Delete" with be used.
   *
   * @property deleteConfirmMessage - The text message which displays to the user (as model dialog)
   * when he|she clicks on "Delete". If omitted, the default, common warning will be shown instead.
   *
   * @property deleteButtonPath - Optional path used when "Delete" button clicked and the deletion
   * of items confirmed. By default, the main request path (inherited from the ProvListProps or
   * ProvTableProps) will be used (with [DELETE] method), but a developer may override that path
   * with the other one.
   *
   * @property itemsSelected - Used for controlled selection of items. If specified - the only
   * a set of items, whose keys are in the provided list, will be selected, and the other ones
   * will not be. So, this property controls whose items to being selected.
   *
   * @property refreshButton - If set to `true` (default) - the "Refresh" button will be rendered,
   * allowing a user to manually refresh the list of items.
   *
   * @property search - If set to `true` - the search text input will be rendered, allowing
   * a user to search over the entity (the entity must have findable fields declared).
   *
   * @property searchArgName - The name of the URL argument used to search over the entity.
   * The "ilike" is used by default.
   *
   * @property searchValue - Used for controlled search inputs; if set - the search text input
   * field will have the exacl {searchValue} value.
   *
   * @property urlStateOffset - If set to `true` & the pagination is enabled - the current offset
   * will be stored to the URL with the default 'offset' argument name; if set to {string} type -
   * the offset will be stored to the URL with given in the 'urlStateOffset' argument name.
   *
   * @property urlStateLimit - If set to `true` & the pagination is enabled - the current limit
   * will be stored to the URL with the default 'limit' argument name; if set to {string} type -
   * the limit will be stored to the URL with given in the 'urlStateLimit' argument name.
   *
   * @property urlStateSort - If set to `true` & sorting options are defined - the current sort
   * will be stored to the URL with the default 'sort' argument name; if set to {string} type -
   * the sort selection will be stored to the URL with given in the 'urlStateSort' argument name.
   *
   * @property urlStateSearch - If set to `true` & search is enabled - the current search term
   * will be stored to the URL with the default 'ilike' argument name; if set to {string} type -
   * the search term will be stored to the URL with given in the 'urlStateSearch' argument name.
   *
   * @property onSearchChange - Optional callback fired on search text input change.
   */

  addButtonAction?: () => void
  addButtonCaption?: string
  addScreenPath?: RequestApiPath
  controls?: JSX.Element | JSX.Element[]
  deleteButtonCaption?: string
  deleteConfirmMessage?: string
  deleteButtonPath?: RequestApiPath | boolean
  itemsSelected?: EnumsSelection
  refreshButton?: boolean
  search?: boolean | string
  searchArgName?: string
  searchValue?: string

  urlStateOffset?: boolean | string
  urlStateLimit?: boolean | string
  urlStateSort?: boolean | string
  urlStateSearch?: boolean | string

  onSearchChange?: (value: string) => void
}

export type EntityListProps = EntityEnumsProps & ProvListProps
export type EntityTableProps = EntityEnumsProps & ProvTableProps

