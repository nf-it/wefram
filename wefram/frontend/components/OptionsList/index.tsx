import React from 'react'
import {
  Box,
  Button,
  CircularBusy,
  CircularProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  LazyTextField,
  MaterialIcon,
  Typography,
} from 'system/components'
import {gettext} from 'system/l10n'
import {CommonKey} from 'system/types'
import {RequestApiPath} from 'system/routing'
import {api} from 'system/api'
import {notifications} from 'system/notification'
import './index.css'


export type OptionsListItem = {
  key: CommonKey,
  caption: string
}
export type OptionsListItems = OptionsListItem[]
export type OptionsResolve = Record<CommonKey, string>


export type OptionsListProps = {
  defaultValues?: CommonKey[]
  emptyMsg?: string | boolean
  items?: OptionsResolve
  gridItemSize?: 0 | 1 | 2 | 3 | 4 | 5 | 6
  name?: string
  resolveItemsPath?: RequestApiPath
  values?: CommonKey[]
  searchItemsPath?: RequestApiPath
  sort?: boolean | ((items: OptionsResolve) => CommonKey[])

  onChange?: (values: CommonKey[]) => void
  onProposionsSearch?: (request: string) => Promise<OptionsResolve>
  onResolveItems?: (keys?: CommonKey[]) => Promise<OptionsResolve>
}

type OptionsListState = {
  items?: Record<CommonKey, string>
  dialogOpen: boolean
  dialogOptionsRequesting: boolean
  dialogOptions: OptionsListItems
  loading: boolean
  values: CommonKey[]
}


export class OptionsList extends React.Component<OptionsListProps, OptionsListState> {
  state: OptionsListState = {
    dialogOpen: false,
    dialogOptionsRequesting: false,
    dialogOptions: [],
    loading: true,
    values: []
  }

  constructor(p: OptionsListProps, s: OptionsListState) {
    super(p, s);
    this.state.values = p.defaultValues || []
  }

  componentDidMount() {
    if (this.props.items !== undefined) {
      this.setState({
        items: this.props.items,
        loading: false
      })
      return
    }
    const values: undefined | CommonKey[] = this.props.values ?? this.props.defaultValues
    if (values === undefined || !values.length) {
      this.setState({loading: false})
      return
    }
    if (this.props.onResolveItems !== undefined) {
      this.props.onResolveItems(this.props.values).then(items => {
        this.setState({items, loading: false})
      })
      return
    }
    if (this.props.resolveItemsPath !== undefined) {
      api.post(this.props.resolveItemsPath, this.props.values).then(res => {
        this.setState({
          items: res.data,
          loading: false
        })
      }).catch(err => {
        notifications.showRequestError(err)
      })
      return
    }
    this.setState({loading: false})
  }

  captionForKey = (key: CommonKey): string => {
    return ((this.props.items ?? {})[key] || (this.state.items ?? {})[key] || key) as string
  }

  closeDialog = () => {
    this.setState({
      dialogOptions: [],
      dialogOpen: false,
      dialogOptionsRequesting: false
    })
  }

  handleDialogSearchComplete = (response: OptionsResolve): void => {
    const options: OptionsListItems = []
    for (let key in response) {
      if (!response.hasOwnProperty(key))
        continue
      options.push({
        key,
        caption: response[key]
      })
    }
    options.sort((a, b) => (a.caption > b.caption) ? 1 : -1)
    this.setState({
      dialogOptions: options.filter((el: OptionsListItem) => !this.state.values.includes(el.key)),
      dialogOptionsRequesting: false
    })
  }

  onDialogSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value: string = e.target.value
    if (!value) {
      this.setState({
        dialogOptions: [],
        dialogOptionsRequesting: false
      })
      return
    }
    this.setState({
      dialogOptionsRequesting: true
    })
    if (this.props.onProposionsSearch !== undefined) {
      this.props.onProposionsSearch(value).then((response: OptionsResolve) => this.handleDialogSearchComplete(response))
    } else if (this.props.searchItemsPath !== undefined) {
      api.options(this.props.searchItemsPath, {
        params: {
          ilike: value
        }
      }).then(res => {
        this.handleDialogSearchComplete(res.data)
      })
    }
  }

  onValueDelete = (key: CommonKey): void => {
    const values: CommonKey[] = (this.props.values ?? this.state.values).filter(el => el !== key)
    this.setState({
      values,
    }, () => {
      this.props.onChange && this.props.onChange(values)
    })
  }

  onAddItem = (item: OptionsListItem): void => {
    const stateItems: OptionsResolve = this.state.items ?? {}
    const propsItems: OptionsResolve = this.props.items ?? {}
    const items: OptionsResolve = {...stateItems, ...propsItems}
    items[item.key] = item.caption

    const values: CommonKey[] = this.props.values ?? this.state.values
    if (!values.includes(item.key)) {
      values.push(item.key)
    }

    const dialogOptions: OptionsListItems = this.state.dialogOptions.filter(el => el.key !== item.key)

    this.setState({
      items,
      values,
      dialogOptions
    }, () => {
      this.props.onChange && this.props.onChange(values)
    })
  }

  render() {
    if (this.state.loading)
      return (
        <CircularBusy />
      )

    let values: CommonKey[] = this.props.values ?? this.state.values

    const stateItems: OptionsResolve = this.state.items ?? {}
    const propsItems: OptionsResolve = this.props.items ?? {}
    const items: OptionsResolve = {...stateItems, ...propsItems}

    if (typeof this.props.sort == 'function') {
      const valitems: OptionsResolve = Object.assign({}, ...values.map((z) => ({[z]: items[z]})))
      values = this.props.sort(valitems)
    } else if (this.props.sort ?? true) {
      values.sort((a, b) => (items[a] > items[b]) ? 1 : -1)
    }

    return (
      <React.Fragment>
        {values.length > 0 && (
          <Grid
            container
            spacing={1}
            direction={(this.props.gridItemSize ?? 0) > 0 ? 'row' : 'column'}
          >
            {values.map((key: CommonKey) => {
              return (
                <Grid item xs={this.props.gridItemSize || 12}>
                  <Chip
                    classes={{
                      root: 'SystemUI-OptionsList-chip-root',
                      label: 'SystemUI-OptionsList-chip-label'
                    }}
                    label={this.captionForKey(key)}
                    onDelete={() => this.onValueDelete(key)}
                    variant={'outlined'}
                  />
                </Grid>
              )
            })}
          </Grid>
        )}
        {values.length == 0 && (this.props.emptyMsg ?? true) !== false && (
          <Box pt={1} pb={1}>
            {typeof this.props.emptyMsg == 'string'
              ? this.props.emptyMsg
              : gettext("The list is empty", 'system.ui')}
          </Box>
        )}
        <Box mt={2} display={'flex'} justifyContent={'flex-end'}>
          <Button
            color={'primary'}
            startIcon={<MaterialIcon icon={'add_circle_outline'} />}
            onClick={() => {
              this.setState({
                dialogOpen: true,
                dialogOptionsRequesting: false,
                dialogOptions: []
              })
            }}
          >{gettext("Add")}</Button>
        </Box>

        <Dialog open={this.state.dialogOpen} onClose={this.closeDialog}>
          <DialogTitle>{gettext("Add elements", 'system.ui')}</DialogTitle>
          <DialogContent style={{minWidth: '500px'}}>
            <Box mb={2}>
              {this.state.dialogOptions.length > 0 ? this.state.dialogOptions.map((opt: OptionsListItem) => (
                <Chip
                  icon={<MaterialIcon icon={'add_circle_outline'} />}
                  label={opt.caption}
                  variant={'outlined'}
                  style={{
                    margin: '4px'
                  }}
                  onClick={() => {
                    this.onAddItem(opt)
                  }}
                />
              )) : (
                <Typography>{gettext("There are no options to display.", 'system.ui')}</Typography>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <LazyTextField
              onChangeLazy={this.onDialogSearch}
              fullWidth
              margin={'dense'}
              placeholder={gettext("Type here to search for options", 'system.ui')}
              variant={'outlined'}
            />
            <Box
                display={'flex'}
                alignItems={'center'}
                justifyContent={'center'}
                minWidth={'32px'}
            >
              {this.state.dialogOptionsRequesting && (
                <CircularProgress
                  size={20}
                  hidden={!this.state.dialogOptionsRequesting}
                />
              )}
            </Box>
            <Button
              color={'primary'}
              onClick={this.closeDialog}
            >{gettext("Close")}</Button>
          </DialogActions>
        </Dialog>
      </React.Fragment>
    )
  }
}
