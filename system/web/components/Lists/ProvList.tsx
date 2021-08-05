import React from 'react'
import {Link} from 'react-router-dom'
import {
  Avatar,
  Box,
  Checkbox,
  Divider,
  FormControl,
  MenuItem,
  Select,
  Tooltip,
  Typography,
  List,
  ListItem,
  ListItemAvatar,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction
} from '@material-ui/core'
import Pagination from '@material-ui/lab/Pagination'
import {
  ListProvidedFilters,
  ListSelection,
  ListSorting,
  ListSortingOptions,
  UrlStateStorage,
  ProvListProps,
  ProvListOverridedParams
} from './types'
import {isEqual} from '../../tools'
import {ListFieldItem} from './ListFieldItem'
import {LoadingLinear} from '../Loading'
import {api} from '../../api'
import {gettext} from '../../l10n'
import {notifications} from '../../notification'
import {IApiEntityResponse, IApiEntityComplexResponse, CommonKey} from '../../types'


type ProvListState = {
  loading: boolean
  pagination: boolean

  items?: any[]
  itemsCount?: number
  itemsCountAll?: number

  sort?: ListSorting | null
  selected?: ListSelection
  offset?: number
  limit?: number

  overridedFilters?: ListProvidedFilters
  overridedParams: ProvListOverridedParams
}


export class ProvList extends React.Component<ProvListProps, ProvListState> {
  state: ProvListState = {
    loading: true,
    pagination: false,
    offset: 0,
    overridedParams: {}
  }

  constructor(p: ProvListProps, s: ProvListState) {
    super(p, s);
    if (p.defaultSort !== undefined) {
      this.state.sort = p.defaultSort
    }
    this.state = this.initStateFromURL(this.state)
    this.fetch()
  }

  shouldComponentUpdate(nextProps: Readonly<ProvListProps>, nextState: Readonly<ProvListState>, nextContext: any): boolean {
    if (!isEqual(nextProps.providedFilters, this.props.providedFilters)) {
      this.fetch(nextProps)
      return false
    }
    return true
  }

  private initStateFromURL = (s: ProvListState): ProvListState => {
    if (this.props.urlStateStorage === undefined)
      return s
    const urlArgs: URLSearchParams = new URLSearchParams(window.location.search)
    const urlStateStorage: UrlStateStorage = this.props.urlStateStorage
    const overridedParams: ProvListOverridedParams = {
      sort: undefined,
      offset: undefined,
      limit: undefined
    }
    if (urlStateStorage.sort) {
      s.sort = this.sortString2Sort(urlArgs.get(urlStateStorage.sort) ?? '') ?? s.sort ?? undefined
      if (s.sort !== undefined) {
        overridedParams.sort = s.sort
      }
    }
    if (urlStateStorage.offset) {
      const offset: string | null = urlArgs.get(urlStateStorage.offset)
      s.offset = (offset !== null ? (Number(offset) || undefined) : undefined) ?? this.props.offset ?? 0
      overridedParams.offset = s.offset
    }
    if (urlStateStorage.limit) {
      const limit: string | null = urlArgs.get(urlStateStorage.limit)
      s.limit = (limit !== null ? (Number(limit) || undefined) : undefined) ?? this.props.limit ?? undefined
      overridedParams.limit = s.limit
    }
    if (urlStateStorage.filters) {
      const providedFilters: ListProvidedFilters = {}
      let filterArgName: string
      let filterArgValue: string | null
      for (let filterName in urlStateStorage.filters) {
        if (!urlStateStorage.filters.hasOwnProperty(filterName))
          continue
        filterArgName = urlStateStorage.filters[filterName]
        filterArgValue = urlArgs.get(filterArgName)
        if (filterArgValue === null)
          continue
        if (filterArgValue === ''
            && (this.props.filtersEmptyAllowed === undefined || !(filterName in this.props.filtersEmptyAllowed)))
          continue
        if (this.props.providedFilters && (filterName in this.props.providedFilters)) {
          providedFilters[filterName] = filterArgValue
        }
      }
      if (Object.keys(providedFilters).length && this.props.onProvidedFiltersUpdateReq) {
        console.log('--1', providedFilters)
        this.props.onProvidedFiltersUpdateReq(providedFilters)
      }
      s.overridedFilters = providedFilters
    }
    return s
  }

  private sortString2Sort = (s: string): ListSorting | undefined => {
    if (!s)
      return undefined
    if (s.startsWith('-'))
      return {
        value: s.substr(1),
        direction: 'desc'
      }
    return {
      value: s,
      direction: 'asc'
    }
  }

  private saveStateToURL = (params: Record<string, any>): void => {
    if (this.props.urlStateStorage === undefined || !Object.keys(this.props.urlStateStorage).length)
      return
    const urlStateStorage: UrlStateStorage = this.props.urlStateStorage
    const urlArgs: URLSearchParams = new URLSearchParams(window.location.search)
    if (urlStateStorage.sort) {
      params.order === undefined || params.order === null
        ? urlArgs.delete(urlStateStorage.sort)
        : urlArgs.set(urlStateStorage.sort, params.order)
    }
    if (urlStateStorage.offset) {
      !params.offset
        ? urlArgs.delete(urlStateStorage.offset)
        : urlArgs.set(urlStateStorage.offset, params.offset)
    }
    if (urlStateStorage.limit) {
      !params.limit
        ? urlArgs.delete(urlStateStorage.limit)
        : urlArgs.set(urlStateStorage.limit, params.limit)
    }
    if (urlStateStorage.filters) {
      let filterArgName: string
      let filterArgValue: string
      for (let filterName in urlStateStorage.filters) {
        if (!urlStateStorage.filters.hasOwnProperty(filterName))
          continue
        filterArgName = urlStateStorage.filters[filterName]
        filterArgValue = params[filterName]
        if (filterArgValue === ''
            && (this.props.filtersEmptyAllowed === undefined || !(filterName in this.props.filtersEmptyAllowed)))
        {
          urlArgs.delete(filterArgName)
          continue
        }
        if (filterArgValue === undefined) {
          urlArgs.delete(filterArgName)
          continue
        }
        urlArgs.set(filterName, String(filterArgValue))
      }
    }
    const args: string = urlArgs.toString()
    const url: string = ''.concat(
      window.location.pathname,
      args ? ''.concat('?', args) : ''
    )
    window.history.replaceState({}, '', url)
  }

  private sort2string = (sort: ListSorting | null | undefined): string => {
    if (sort === null || sort === undefined)
      return ''
    return ''.concat(
      sort.direction !== 'asc' ? '-' : '',
      sort.value
    )
  }

  public fetch = (useProps?: ProvListProps): void => {
    this.setState({loading: true})

    const
      props: ProvListProps = useProps ?? this.props,
      params: Record<string, any> = {},
      sort: ListSorting | null =
        this.state.overridedParams.sort
        ?? props.sort
        ?? this.state.sort
        ?? null,
      offset: number | null =
        this.state.overridedParams.offset
        ?? props.offset
        ?? this.state.offset
        ?? null,
      limit: number | null =
        this.state.overridedParams.limit
        ?? props.limit
        ?? this.state.limit
        ?? null

    for (let n in props.providedFilters) {
      if (!props.providedFilters.hasOwnProperty(n))
        continue
      let v = props.providedFilters[n]
      if (v === '' && (props.filtersEmptyAllowed === undefined || !props.filtersEmptyAllowed.includes(n)))
        continue
      params[n] = v
    }
    if (this.state.overridedFilters) {
      for (let n in this.state.overridedFilters) {
        if (!this.state.overridedFilters.hasOwnProperty(n))
          continue
        let v = this.state.overridedFilters[n]
        if (v === '' && (props.filtersEmptyAllowed === undefined || !props.filtersEmptyAllowed.includes(n)))
          continue
        params[n] = v
      }
    }

    if (sort !== null) {
      params['order'] = this.sort2string(sort)
    }
    if (props.pagination && offset !== null && limit !== null) {
      params['offset'] = Number(offset)
      params['limit'] = Number(limit)
      params['count'] = true
    }

    this.saveStateToURL(params)

    api.get(props.requestPath, {
      params
    }).then(res => {

      this.setState({loading: false})
      props.onFetch ? props.onFetch(res.data) : this.handleFetch(res.data)
    }).catch(err => {

      this.setState({loading: false}, () => {
        this.props.onFetchDone && this.props.onFetchDone(false)
      })
      if (props.onError) {
        props.onError(err)
      } else if (props.onErrorShowMsg ?? true) {
        const msg: string = typeof props.onErrorShowMsg === 'string'
          ? props.onErrorShowMsg
          : props.entityCaption
            ? [
              `${gettext('An error occurred while fetching data from the server', 'system.ui-common')}`,
              props.entityCaption
            ].join(': ')
            : `${gettext('An error occurred while fetching data from the server', 'system.ui-common')}`
        notifications.showError(msg)
      }
    })
  }

  private handleFetch = (response: IApiEntityResponse | IApiEntityComplexResponse): void => {
    if (Array.isArray(response)) {
      this.setState({
        items: response,
        itemsCount: undefined,
        itemsCountAll: undefined,
        overridedFilters: undefined,
        overridedParams: {
          sort: undefined,
          offset: undefined,
          limit: undefined
        }
      }, () => {
        this.props.onFetchDone && this.props.onFetchDone()
      })
    } else {
      this.setState({
        items: response.items,
        itemsCount: response.itemsCount,
        itemsCountAll: response.itemsCountAll,
        overridedFilters: undefined,
        overridedParams: {
          sort: undefined,
          offset: undefined,
          limit: undefined
        }
      }, () => {
        this.props.onFetchDone && this.props.onFetchDone(true)
      })
    }
  }

  private handleCheckboxChange = (key: CommonKey): void => {
    const selected = (this.props.selected ?? this.state.selected ?? []) as any
    const checked = selected.includes(key)
    if (checked) {
      selected.splice(selected.indexOf(key), 1)
    } else {
      selected.push(key)
    }
    this.props.onSelection !== undefined
      ? this.props.onSelection(selected)
      : this.setState({selected})
  }

  public invertSelection = (): void => {
    const items = this.props.items ?? this.state.items ?? []
    const currentSelected = (this.props.selected ?? this.state.selected ?? []) as any
    const updatedSelected: any[] = []
    items.forEach(item => {
      const key: number | string | undefined =
        this.props.itemKeyField
          ? item[this.props.itemKeyField]
          : (item.key ?? item.id)
      if (key === undefined)
        return
      const selected: boolean = currentSelected.includes(key)
      if (!selected) {
        updatedSelected.push(key)
      }
    })
    this.props.onSelection !== undefined
      ? this.props.onSelection(updatedSelected)
      : this.setState({selected: updatedSelected})
  }

  private handlePaginationChange = (e: any, page: number): void => {
    const limit: number | null = this.props.limit ?? this.state.limit ?? null
    if (limit === null)
      return
    const cb: any = this.props.onPageChange !== undefined
      ? () => {
        this.props.onPageChange !== undefined && this.props.onPageChange(page, this.fetch)
      } : this.fetch
    this.setState({
      offset: limit * (page-1)
    }, cb)
  }

  private handleSortChange = (e: React.ChangeEvent<{ value: unknown }>): void => {
    const value: string = e.target.value as string
    const sort: ListSorting | null = value === 'null' ? null : {
      value: value.startsWith('-') ? value.substr(1) : value,
      direction: value.startsWith('-') ? 'desc' : 'asc'
    }
    const cb: any = this.props.onSortChange !== undefined
      ? () => {
        this.props.onSortChange !== undefined && this.props.onSortChange(sort, this.fetch)
      } : this.fetch
    this.setState({
      sort
    }, cb)
  }

  private sortValueOf = (sort?: ListSorting | null): string => {
    if (sort === undefined || sort === null)
      return 'null'
    return ''.concat(
      sort.direction === 'desc' ? '-' : '',
      sort.value
    )
  }

  private getItemAlt = (item: any): string | undefined => {
    if (typeof this.props.primaryField == 'string')
      return item[this.props.primaryField]
    return undefined
  }

  private getItemAvatarUrl = (item: any): string | null => {
    return this.props.avatarField && item[this.props.avatarField] !== undefined
      ? item[this.props.avatarField]
      : null
  }

  render() {
    if (this.state.items === undefined)
      return (
        <LoadingLinear />
      )

    const
      items = (this.props.items ?? this.state.items) || [],
      limit: number | null = this.props.limit ?? this.state.limit ?? null,
      offset: number | null = this.props.offset ?? this.state.offset ?? null,
      sort: ListSorting | undefined = this.props.sort ?? this.state.sort ?? undefined,
      sortValue: string = this.sortValueOf(sort),
      sortOptions: ListSortingOptions = this.props.sortOptions || [],

      pages: number | null = this.state.itemsCount !== undefined && limit !== null
        ? Math.ceil(this.state.itemsCount / limit)
        : null,
      page: number | null = this.state.itemsCount !== undefined && limit !== null && offset !== null
        ? Math.floor(offset / limit) + 1
        : null

    return (
      <Box>
        <Box
          hidden={!this.state.loading}
          position={'absolute'}
          left={0}
          top={0}
          right={0}
          bottom={0}
          zIndex={10}
          style={{
            backgroundColor: '#ffffff44'
          }}
        >
          <LoadingLinear />
        </Box>

        <Box
          mt={1} mb={1}
          pl={2}
          display={'flex'} flexDirection={'row'} alignItems={'center'}
        >
          {this.props.selectable === true && (
            <Box mr={3}>
              <Tooltip title={gettext("Invert selection", 'system.ui')}>
                <Checkbox
                  edge="start"
                  checked={true}
                  tabIndex={-1}
                  disableRipple
                  onClick={this.invertSelection}
                />
              </Tooltip>
            </Box>
          )}

          {(this.props.textTotalCount ?? false) !== false && this.state.itemsCount !== undefined && (
            <Box component={'span'} mr={4}>
              {this.props.textTotalCount === true && gettext("Total rows", 'system.ui')}
              {': '}
              {this.state.itemsCount}
            </Box>
          )}

          {sortOptions.length > 0 && (
            <React.Fragment>
              <Box component={'span'} mr={2}>{gettext("Sort by", 'system.ui')}:</Box>
              <FormControl variant={'outlined'} size={'small'}>
                <Select
                  autoWidth
                  className={'mr-4'}
                  onChange={this.handleSortChange}
                  value={sortValue}
                >
                  {this.props.unsortedOption !== undefined && (
                    <MenuItem value={'null'}>
                      {typeof this.props.unsortedOption == 'string' ? this.props.unsortedOption : gettext("Unsorted", 'system.ui')}
                    </MenuItem>
                  )}
                  {sortOptions.map(option => ([
                    <MenuItem value={String(option.value)}>
                      {option.caption} {'\u2191'}
                    </MenuItem>,
                    <MenuItem value={String(`-${option.value}`)}>
                     {option.caption} {'\u2193'}
                    </MenuItem>
                  ]))}
                </Select>
              </FormControl>
            </React.Fragment>
          )}

          {this.props.pagination === true && pages !== null && (pages > 2) && page !== null && (
            <Box
              display={'flex'}
              flexGrow={1}
              justifyContent={'flex-end'}
              minWidth={'320px'}
            >
              <Pagination
                count={pages}
                page={page}
                onChange={this.handlePaginationChange}
                siblingCount={1}
              />
            </Box>
          )}
        </Box>

        {items.length === 0 && this.props.emptyListText !== false && (
          <Typography className={'SystemUI-Lists EmptyList'}>
            {gettext("The list is empty.", 'system.ui')}
          </Typography>
        )}

        {items.length > 0 && (
          <List className={'SystemUI-Lists List'}>
            {items.map((item, index) => {

              const
                keyRe = /{key}/g,
                key: number | string | undefined = this.props.itemKeyField
                  ? item[this.props.itemKeyField]
                  : (item.key ?? item.id),
                itemsRoute = this.props.itemsRoute,
                routePath: string | null =
                  (key && itemsRoute)
                    ? (typeof itemsRoute == 'string'
                      ? String(itemsRoute).replace(keyRe, String(key))
                      : itemsRoute(item)
                    ) : null,
                divider: boolean = index < items.length - 1,
                primaryField: string = this.props.primaryField ?? 'caption',
                itemAltText: string | undefined = this.getItemAlt(item),
                avatarUrl: string | null = this.getItemAvatarUrl(item),
                selection = (this.props.selected ?? this.state.selected ?? []) as any[],
                selected: boolean = (key !== undefined && this.props.selectable && selection.length)
                  ? selection.includes(key)
                  : false

              const PrimaryFieldComponent = this.props.primaryComponent || ListFieldItem
              const SecondaryFieldComponent = this.props.secondaryComponent || ListFieldItem

              const ListItemComponent: React.ElementType | undefined = this.props.itemComponent
              const ListItemElement = ListItemComponent !== undefined
                ? (
                  <ListItemComponent
                    item={item}
                    index={index}
                    offset={offset}
                    limit={limit}
                    sort={sort}
                  />
                ) : (
                  <React.Fragment>
                    <ListItem button>
                      {avatarUrl !== null && (
                        <ListItemAvatar>
                          <Avatar alt={itemAltText} src={avatarUrl}/>
                        </ListItemAvatar>
                      )}
                      {key !== undefined && avatarUrl === null && this.props.selectable === true && (
                        <ListItemIcon>
                          <Checkbox
                            edge="start"
                            checked={selected}
                            tabIndex={-1}
                            disableRipple
                            inputProps={{'aria-labelledby': String(key)}}
                            value={key}
                            onClick={e => {
                              e.preventDefault()
                              e.stopPropagation()
                              this.handleCheckboxChange(key)
                            }}
                            /*onChange={() => this.handleCheckboxChange(key)}*/
                          />
                        </ListItemIcon>
                      )}

                      <ListItemText
                        primary={<PrimaryFieldComponent item={item} field={primaryField} />}
                        secondary={this.props.secondaryField && (
                          <SecondaryFieldComponent item={item} field={this.props.secondaryField} />
                        )}
                      />

                      {(key !== undefined && this.props.selectable && this.props.avatarField) && (

                        <ListItemSecondaryAction>
                          <Checkbox
                            edge="start"
                            checked={selected}
                            tabIndex={-1}
                            disableRipple
                            inputProps={{'aria-labelledby': String(key)}}
                            onClick={e => {
                              e.stopPropagation()
                            }}
                            onChange={() => this.handleCheckboxChange(key)}
                          />
                        </ListItemSecondaryAction>
                      )}

                    </ListItem>
                    {divider && <Divider />}
                  </React.Fragment>
                )

              return routePath
                ? <Link to={routePath} className={'SystemUI-Lists RouteLink'}>{ListItemElement}</Link>
                : this.props.onItemClick !== undefined
                  ? <Box onClick={() => this.props.onItemClick && this.props.onItemClick(item)}>{ListItemElement}</Box>
                  : <React.Fragment>{ListItemElement}</React.Fragment>
            })}
          </List>
        )}

        <Box
          mt={1}
          mb={1}
          pb={2}
          display={'flex'}
          alignItems={'center'}
          justifyContent={'center'}
        >
          {this.props.pagination === true && pages !== null && (pages > 2) && page !== null && (
            <Pagination
              count={pages}
              page={page}
              onChange={this.handlePaginationChange}
              siblingCount={2}
              showFirstButton={true}
              showLastButton={true}
            />
          )}
        </Box>
      </Box>
    )
  }
}
