import React, {createRef} from 'react'
import {
  Box,
  Button,
  ButtonLink,
  IconButton,
  InputAdornment,
  LazyTextField,
  ListsProvidedFilters,
  ListsSelection,
  MaterialIcon,
  Paper,
  ProvList,
  ProvListProps,
  Tooltip
} from 'system/components'
import {gettext} from 'system/l10n'
import {dialog} from 'system/dialog'
import {api} from 'system/api'
import {notifications} from 'system/notification'
import {RequestApiPath} from 'system/routing'
import {UrlStateStorage} from 'system/components/Lists/types'


export interface EntityListProps extends ProvListProps {
  search?: boolean | string
  searchArgName?: string
  addScreen?: RequestApiPath
  addButtonCaption?: string
  addButtonAction?: () => void
  controls?: JSX.Element | JSX.Element[]
  deleteButton?: RequestApiPath | boolean
  deleteButtonCaption?: string
  deleteConfirmMessage?: string
  itemsSelected?: ListsSelection
  refreshButton?: boolean
  urlStateOffset?: boolean | string
  urlStateLimit?: boolean | string
  urlStateSort?: boolean | string
  urlStateSearch?: boolean | string
}


type EntityListState = {
  searchValue: string
  searchLazyValue: string
  itemsSelected: ListsSelection
}


export class EntityList extends React.Component<EntityListProps, EntityListState> {
  state: EntityListState = {
    searchValue: "",
    searchLazyValue: "",
    itemsSelected: []
  }

  private listRef = createRef<ProvList>()

  onItemsSelection = (itemsSelected: ListsSelection): void => {
    this.setState({itemsSelected})
  }

  public update = (): void => {
    this.listRef.current?.fetch()
  }

  render() {
    const
      providedFilters: ListsProvidedFilters = {},
      itemsSelected: ListsSelection = this.props.itemsSelected ?? this.state.itemsSelected
    let
      urlStateStorage: UrlStateStorage | undefined = this.props.urlStateStorage ?? {}

    if (this.props.search) {
      providedFilters[this.props.searchArgName ?? 'ilike'] = this.state.searchLazyValue
      if (this.props.urlStateSearch) {
        urlStateStorage.filters = urlStateStorage.filters ?? {}
        urlStateStorage.filters[this.props.searchArgName ?? 'ilike'] =
          typeof this.props.urlStateSearch == 'boolean'
            ? 'search'
            : this.props.urlStateSearch
      }
    }
    if (this.props.providedFilters) {
      for (let k in this.props.providedFilters) {
        if (!this.props.providedFilters.hasOwnProperty(k))
          continue
        providedFilters[k] = this.props.providedFilters[k]
      }
    }

    if (this.props.urlStateSort) {
      urlStateStorage.sort = typeof this.props.urlStateSort == 'boolean'
        ? 'sort'
        : this.props.urlStateSort
    }
    if (this.props.urlStateLimit) {
      urlStateStorage.limit = typeof this.props.urlStateLimit == 'boolean'
        ? 'limit'
        : this.props.urlStateLimit
    }
    if (this.props.urlStateOffset) {
      urlStateStorage.offset = typeof this.props.urlStateOffset == 'boolean'
        ? 'offset'
        : this.props.urlStateOffset
    }

    const
      refreshButton = this.props.refreshButton !== false && (
        this.props.search !== undefined
          || this.props.addScreen !== undefined
          || this.props.deleteButton !== undefined
          || this.props.controls !== undefined
      )
    const
      controlsBox =
        this.props.search !== undefined
        || this.props.addScreen !== undefined
        || this.props.deleteButton !== undefined
        || this.props.controls !== undefined
        || refreshButton

    return (
      <Paper variant={'outlined'}>
        {controlsBox && (
          <Box display={'flex'} flexDirection={'row'} justifyContent={'flex-end'} p={2} mt={2} mb={2}>
            {this.props.search !== undefined && (
              <LazyTextField
                label={gettext("Find")}
                placeholder={this.props.search === true ? gettext("Type here to find...") : String(this.props.search)}
                value={this.state.searchValue}
                fullWidth
                variant={'outlined'}
                size={'small'}
                onChange={event => this.setState({searchValue: event.target.value})}
                onChangeLazy={event => this.setState({searchLazyValue: event.target.value})}
                color={this.state.searchValue ? 'success' : undefined}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position={'end'}>
                      <IconButton
                          size={'small'}
                          onClick={() => this.setState(
                            {searchValue: '', searchLazyValue: ''}
                          )}
                      >
                        <MaterialIcon icon={'backspace'} />
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
            )}

            {this.props.addScreen !== undefined && (
              <Box ml={1}>
                <ButtonLink
                  to={api.pathToUrl(this.props.addScreen)}
                  variant={'outlined'}
                  color={'primary'}
                >
                  {this.props.addButtonCaption ?? gettext("Add")}
                </ButtonLink>
              </Box>
            )}
            {!Boolean(this.props.addScreen) && this.props.addButtonAction !== undefined && (
              <Box ml={1}>
                <Button
                  variant={'outlined'}
                  color={'primary'}
                  onClick={this.props.addButtonAction}
                >
                  {this.props.addButtonCaption ?? gettext("Add")}
                </Button>
              </Box>
            )}

            {this.props.deleteButton !== undefined && this.props.deleteButton !== false && (
              <Box ml={1}>
                <Tooltip title={this.props.deleteButtonCaption ?? gettext("Delete")}>
                  <Button
                    onClick={() => {
                      dialog.showConfirm({
                        message: this.props.deleteConfirmMessage
                          ?? gettext("Are you sure you want to delete?"),
                        captionOK: gettext("Delete"),
                        colorOK: 'secondary',
                        okCallback: () => {
                          dialog.setBusy(true)
                          api.deleteObjects(
                            typeof this.props.deleteButton == 'boolean'
                              ? this.props.requestPath
                              : this.props.deleteButton as RequestApiPath,
                            this.state.itemsSelected
                          )
                            .then(res => {
                              dialog.hide()
                              notifications.showRequestSuccess(res)
                              this.listRef.current?.fetch()
                            })
                            .catch(err => {
                              dialog.setBusy(false)
                              notifications.showRequestError(err)
                            })
                        }
                      })
                    }}
                    color={'secondary'}
                    variant={'outlined'}
                    disabled={this.state.itemsSelected.length === 0}
                  >
                    <MaterialIcon icon={'delete'} />
                  </Button>
                </Tooltip>
              </Box>
            )}

            {refreshButton && (
              <Box ml={1}>
                <Button
                  color={'primary'}
                  variant={'outlined'}
                  onClick={() => this.listRef.current?.fetch()}
                >
                  <MaterialIcon icon={'refresh'} />
                </Button>
              </Box>
            )}
          </Box>
        )}

        <Box pl={this.props.variant === 'cards' ? 2 : 0} pr={this.props.variant === 'cards' ? 2 : 0}>
          <ProvList
            ref={this.listRef}
            providedFilters={providedFilters}
            selected={itemsSelected}
            urlStateStorage={urlStateStorage}
            onSelection={this.onItemsSelection}
            onProvidedFiltersUpdateReq={(filters => {
              this.setState({
                searchValue: filters['ilike'],
                searchLazyValue: filters['ilike']
              })
            })}
            {...this.props}
          />
        </Box>
      </Paper>
    )
  }
}
