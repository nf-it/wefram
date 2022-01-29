import React, {createRef} from 'react'
import {
  Box,
  Button,
  ButtonLink,
  IconButton,
  InputAdornment,
  LazyTextField,
  EnumsProvidedFilters,
  EnumsSelection,
  MaterialIcon,
  Paper,
  ProvList,
  Tooltip
} from 'system/components'
import {gettext} from 'system/l10n'
import {dialog} from 'system/dialog'
import {api} from 'system/api'
import {notifications} from 'system/notification'
import {RequestApiPath} from 'system/routing'
import {UrlStateStorage} from 'system/components/ProvEnums/types'
import {EntityListProps} from './types'


type EntityListState = {
  searchValue: string
  searchLazyValue: string
  itemsSelected: EnumsSelection
}


export class EntityList extends React.Component<EntityListProps, EntityListState> {
  state: EntityListState = {
    searchValue: "",
    searchLazyValue: "",
    itemsSelected: []
  }

  private listRef = createRef<ProvList>()

  onItemsSelection = (itemsSelected: EnumsSelection): void => {
    this.setState({itemsSelected})
  }

  public update = (): void => {
    this.listRef.current?.fetch()
  }

  render() {
    const
      providedFilters: EnumsProvidedFilters = {},
      itemsSelected: EnumsSelection = this.props.itemsSelected ?? this.state.itemsSelected
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
          || this.props.addScreenPath !== undefined
          || this.props.deleteAction !== undefined
          || this.props.controls !== undefined
      )
    const
      controlsBox =
        this.props.search !== undefined
        || this.props.addScreenPath !== undefined
        || this.props.deleteAction !== undefined
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
                onChange={event => this.setState(
                  {searchValue: event.target.value},
                  () => this.props.onSearchChange && this.props.onSearchChange(event.target.value)
                )}
                onChangeLazy={event => this.setState({searchLazyValue: event.target.value})}
                color={this.state.searchValue ? 'success' : undefined}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position={'end'}>
                      <IconButton
                          size={'small'}
                          onClick={() => this.setState(
                            {searchValue: '', searchLazyValue: ''},
                            () => this.props.onSearchChange && this.props.onSearchChange('')
                          )}
                      >
                        <MaterialIcon icon={'backspace'} />
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
            )}

            {Array.isArray(this.props.controls) ? this.props.controls.map((el: React.ReactNode) => (
              <Box ml={1} display={'flex'}>{el}</Box>
            )) : this.props.controls !== null && this.props.controls !== undefined ? (
              <Box ml={1} display={'flex'}>{this.props.controls}</Box>
            ) : null}

            {this.props.addScreenPath !== undefined && (
              <Box ml={1} display={'flex'}>
                <ButtonLink
                  to={api.pathToUrl(this.props.addScreenPath)}
                  variant={'outlined'}
                  color={'primary'}
                >
                  {this.props.addButtonCaption ?? gettext("Add")}
                </ButtonLink>
              </Box>
            )}
            {!Boolean(this.props.addScreenPath) && this.props.addButtonAction !== undefined && (
              <Box ml={1} display={'flex'}>
                <Button
                  variant={'outlined'}
                  color={'primary'}
                  onClick={this.props.addButtonAction}
                >
                  {this.props.addButtonCaption ?? gettext("Add")}
                </Button>
              </Box>
            )}

            {this.props.deleteAction !== undefined && this.props.deleteAction !== false && (
              <Box ml={1} display={'flex'}>
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
                            typeof this.props.deleteAction == 'boolean'
                              ? this.props.requestPath
                              : this.props.deleteAction as RequestApiPath,
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
              <Box ml={1} display={'flex'}>
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
