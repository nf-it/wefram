import React from 'react'
import {
  Box,
  Button,
  Checkbox,
  DividerRuler,
  MenuItem,
  TextField,
  Tooltip,
  Typography,
  Pagination
} from 'system/components'
import {
  ListsProvidedFilters,
  ListsSelection,
  ListsSorting,
  ListsSortingOptions,
  UrlStateStorage,
  ProvListProps,
  ProvListOverridedParams,
  ProvTableProps,
  ProvTableOverridedParams
} from './types'
import {isEqual} from 'system/tools'
import {LoadingLinear} from '../Loading'
import {api} from 'system/api'
import {gettext} from 'system/l10n'
import {notifications} from 'system/notification'
import {IApiEntityResponse, IApiEntityComplexResponse} from 'system/types'
import {responses} from 'system/response'


export type ProvHocFetchResult = {
  items?: any[]
  itemsCount?: number
  itemsCountAll?: number
}

export type ProvHocProps = (ProvTableProps | ProvListProps) & {
  disableSelectInvertButton?: boolean
  onHocFetch: (state: ProvHocFetchResult) => void
  onHocInvertSelection?: () => void
}

type ProvHocOverridedParams = ProvTableOverridedParams | ProvListOverridedParams

type ProvHocState = {
  loading: boolean
  pagination: boolean

  itemsCount?: number
  itemsCountAll?: number
  error: string | null

  sort?: ListsSorting | null
  selected?: ListsSelection
  offset?: number
  limit?: number

  overridedFilters?: ListsProvidedFilters
  overridedParams: ProvHocOverridedParams
}


export class ProvListsHoc extends React.Component<ProvHocProps, ProvHocState> {
  state: ProvHocState = {
    loading: true,
    pagination: false,
    offset: 0,
    overridedParams: {},
    error: null
  }

  constructor(p: ProvHocProps, s: ProvHocState) {
    super(p, s);
    if (p.defaultSort !== undefined) {
      this.state.sort = p.defaultSort
    }
    this.state = this.initStateFromURL(this.state)
    this.fetch()
  }

  shouldComponentUpdate(nextProps: Readonly<ProvHocProps>, nextState: Readonly<ProvHocState>, nextContext: any): boolean {
    if (!isEqual(nextProps.providedFilters, this.props.providedFilters)) {
      this.fetch(nextProps, true)
      return false
    }
    return true
  }

  private initStateFromURL = (s: ProvHocState): ProvHocState => {
    if (this.props.urlStateStorage === undefined)
      return s
    const urlArgs: URLSearchParams = new URLSearchParams(window.location.search)
    const urlStateStorage: UrlStateStorage = this.props.urlStateStorage
    const overridedParams: ProvTableOverridedParams = {
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
      const providedFilters: ListsProvidedFilters = {}
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
        this.props.onProvidedFiltersUpdateReq(providedFilters)
      }
      s.overridedFilters = providedFilters
    }
    return s
  }

  private sortString2Sort = (s: string): ListsSorting | undefined => {
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

  private sort2string = (sort: ListsSorting | null | undefined): string => {
    if (sort === null || sort === undefined)
      return ''
    return ''.concat(
      sort.direction !== 'asc' ? '-' : '',
      sort.value
    )
  }

  public fetch = (useProps?: ProvHocProps, forceZeroOffset: boolean = false): void => {
    this.setState({
      loading: true
    })
    if (forceZeroOffset) {
      this.setState({
        offset: 0
      })
    }

    const
      props: ProvHocProps = useProps ?? this.props,
      params: Record<string, any> = {},
      sort: ListsSorting | null =
        this.state.overridedParams.sort
        ?? props.sort
        ?? this.state.sort
        ?? null,
      offset: number | null =
        forceZeroOffset
          ? 0
          : this.state.overridedParams.offset
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
      this.setState({loading: false, error: null})
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
      const error: string = responses.responseErrorMessage(err)
      this.setState({error})
    })
  }

  private handleFetch = (response: IApiEntityResponse | IApiEntityComplexResponse): void => {
    if (Array.isArray(response)) {
      this.setState({
        itemsCount: undefined,
        itemsCountAll: undefined,
        overridedFilters: undefined,
        overridedParams: {
          sort: undefined,
          offset: undefined,
          limit: undefined
        }
      }, () => {
        this.props.onHocFetch({
          items: response,
          itemsCount: undefined,
          itemsCountAll: undefined
        })
        this.props.onFetchDone && this.props.onFetchDone()
      })
    } else {
      this.setState({
        itemsCount: response.itemsCount,
        itemsCountAll: response.itemsCountAll,
        overridedFilters: undefined,
        overridedParams: {
          sort: undefined,
          offset: undefined,
          limit: undefined
        }
      }, () => {
        this.props.onHocFetch({
          items: response.items,
          itemsCount: undefined,
          itemsCountAll: undefined
        })
        this.props.onFetchDone && this.props.onFetchDone(true)
      })
    }
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

  private handleSortChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const value: string = e.target.value as string
    const sort: ListsSorting | null = value === 'null' ? null : {
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

  private sortValueOf = (sort?: ListsSorting | null): string => {
    if (sort === undefined || sort === null)
      return 'null'
    return ''.concat(
      sort.direction === 'desc' ? '-' : '',
      sort.value
    )
  }

  render() {
    if (this.state.error !== null)
      return (
        <Box mt={3} mb={3} pb={3} textAlign={'center'}>
          <Typography variant={'body2'} style={{color: '#b30'}}>
            {this.state.error}
          </Typography>
          <DividerRuler vspace={2} />
          <Box display={'flex'} justifyContent={'center'}>
            <Button
              color={'primary'}
              variant={'outlined'}
              onClick={() => this.fetch()}
            >{gettext("Try again", 'system.ui')}</Button>
          </Box>
        </Box>
      )

    if (this.props.items === undefined)
      return (
        <LoadingLinear />
      )

    const
      items = this.props.items || [],
      limit: number | null = this.props.limit ?? this.state.limit ?? null,
      offset: number | null = this.props.offset ?? this.state.offset ?? null,
      sort: ListsSorting | undefined = this.props.sort ?? this.state.sort ?? undefined,
      sortValue: string = this.sortValueOf(sort),
      sortOptions: ListsSortingOptions = this.props.sortOptions || [],

      pages: number | null = this.state.itemsCount !== undefined && limit !== null
        ? Math.ceil(this.state.itemsCount / limit)
        : null,
      page: number | null = this.state.itemsCount !== undefined && limit !== null && offset !== null
        ? Math.floor(offset / limit) + 1
        : null

    return (
      <Box className={'SystemUI-Lists'}>
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
          {this.props.selectable === true && (!this.props.disableSelectInvertButton) && (
            <Box mr={3}>
              <Tooltip title={gettext("Invert selection", 'system.ui')}>
                <Checkbox
                  edge="start"
                  checked={true}
                  tabIndex={-1}
                  disableRipple
                  onClick={() => (this.props.onHocInvertSelection && this.props.onHocInvertSelection())}
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
            <Box mr={4}>
              <TextField
                select
                label={gettext("Sort by", 'system.ui')}
                onChange={this.handleSortChange}
                value={sortValue}
                size={'small'}
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
              </TextField>
            </Box>
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
          <Typography className={'EmptyList'} style={{paddingTop: '16px'}}>
            {gettext("The list is empty", 'system.ui')}
          </Typography>
        )}

        {items.length > 0 && this.props.children}

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
