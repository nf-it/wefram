import React, {createRef} from 'react'
import {
  Box,
  Button,
  Paper,
  Tooltip
} from '@material-ui/core'
import DeleteIcon from '@material-ui/icons/Delete'
import {
  ButtonLink,
  LazyTextField,
  ProvList,
  ProvListProps
} from '../../components'
import {ListProvidedFilters, ListSelection} from '../../components'
import {gettext} from '../../l10n'
import {dialog} from '../../dialog'
import {api} from '../../api'
import {notifications} from '../../notification'
import {RequestApiPath} from '../../routing'
import {UrlStateStorage} from '../../components/Lists/types'


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
  itemsSelected?: ListSelection
  urlStateOffset?: boolean | string
  urlStateLimit?: boolean | string
  urlStateSort?: boolean | string
  urlStateSearch?: boolean | string
}


type EntityListState = {
  searchValue: string
  searchLazyValue: string
  itemsSelected: ListSelection
}


export class EntityList extends React.Component<EntityListProps, EntityListState> {
  state: EntityListState = {
    searchValue: "",
    searchLazyValue: "",
    itemsSelected: []
  }

  private listRef = createRef<ProvList>()

  onItemsSelection = (itemsSelected: ListSelection): void => {
    this.setState({itemsSelected})
  }

  public update = (): void => {
    this.listRef.current?.fetch()
  }

  render() {
    const
      providedFilters: ListProvidedFilters = this.props.providedFilters || {},
      itemsSelected: ListSelection = this.props.itemsSelected ?? this.state.itemsSelected
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

    return (
      <React.Fragment>
        {this.props.search !== undefined && (
          <LazyTextField
            placeholder={this.props.search === true ? gettext("Type here to find...") : String(this.props.search)}
            value={this.state.searchValue}
            fullWidth
            onChange={event => this.setState({searchValue: event.target.value})}
            className={'mt-3 mb-3'}
            onChangeLazy={event => this.setState({searchLazyValue: event.target.value})}
          />
        )}

        <Paper elevation={2}>
          {(this.props.addScreen !== undefined
            || this.props.deleteButton !== undefined
            || this.props.controls !== undefined) &&
          (
            <Box display={'flex'} flexDirection={'row'} justifyContent={'flex-end'} p={2}>
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
                      <DeleteIcon />
                    </Button>
                  </Tooltip>
                </Box>
              )}
            </Box>
          )}

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
        </Paper>
      </React.Fragment>
    )
  }
}
