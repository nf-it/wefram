import React from 'react'
import {
  Backdrop,
  Box,
  Button,
  CircularProgress,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Toolbar,
  Tooltip,
  Typography
} from '@material-ui/core'
import BackIcon from '@material-ui/icons/ArrowBackIosRounded'
import SubmitIcon from '@material-ui/icons/DoneRounded'
import DeleteIcon from '@material-ui/icons/DeleteRounded'
import {api} from '../../api'
import {TApiSubmitMethod} from '../../types'
import {RequestApiPath, RequestMethod, routing} from '../../routing'
import {LoadingLinear} from '../../components'
import {CommonKey, IApiEntityComplexResponse, IApiEntityResponse} from '../../types'
import {notifications} from '../../notification'
import {dialog} from '../../dialog'
import {Permissions} from '../../aaa'
import {gettext} from '../../l10n'


type ReactElements = any | any[] | null | undefined
export type EntityData = Record<string, any>

export type EntityFormProps = {
  close?: string | boolean
  data: EntityData
  delete?: string | boolean
  deleteDisabled?: boolean
  deletePath?: RequestApiPath | string
  deleteMethod?: RequestMethod
  deleteRequres?: Permissions
  entityName?: string
  entityKey?: string | null
  stateDataName?: string
  requestPath?: RequestApiPath | string
  requiredForSubmit?: string[]
  submit?: string | boolean
  submitDisabled?: boolean
  submitPath?: RequestApiPath | string
  submitMethod?: RequestMethod
  submitRequres?: Permissions
  submitFieldsModel?: string[]
  title?: string
  variant?: 'outlined' | 'embedded'
  windowed?: boolean

  onAfterDelete?: () => void
  onAfterSubmit?: () => void
  onClose?: () => void
  onUpdateData: (data: EntityData, cb?: any) => void
  onError?: (err: any) => void
  onErrorShowMsg?: boolean | string
  onFetch?: (response: IApiEntityResponse | IApiEntityComplexResponse) => void
}

type EntityFormState = {
  dirty: boolean
  loading: boolean
  success: boolean
  submitting: boolean
  dataInitial: EntityData
}


export class EntityForm extends React.Component<EntityFormProps, EntityFormState> {
  state: EntityFormState = {
    dirty: false,
    loading: true,
    success: false,
    submitting: false,
    dataInitial: {}
  }

  componentDidMount() {
    if (!this.props.requestPath || !this.props.entityKey) {
      this.setState({
        loading: false,
        success: true
      })
      return
    }
    this.fetch()
  }

  public close = (): void => {
    this.props.onClose !== undefined
      ? this.props.onClose()
      : (!this.props.windowed)
        ? routing.back()
        : null
  }

  private afterSubmit = (): void => {
    this.props.onAfterSubmit !== undefined
      ? this.props.onAfterSubmit()
      : this.close()
  }

  private afterDelete = (): void => {
    this.props.onAfterDelete !== undefined
      ? this.props.onAfterDelete()
      : this.close()
  }

  public submit = (): void => {
    const key: CommonKey | undefined =
      this.props.entityKey !== null
      ? this.props.entityKey
      : undefined
    const submitPath: RequestApiPath | null =
      this.props.submitPath
      ?? this.props.requestPath
      ?? null;
    if (submitPath === null)
      return

    const submitMethod: TApiSubmitMethod =
      ((this.props.submitMethod ?? (key ? 'PUT' : 'POST')).toUpperCase()) as TApiSubmitMethod

    if (! ['PUT', 'POST'].includes(submitMethod))
      throw (`FormEntity.submit() - submit method ${submitMethod} is not supported!`)

    const submitData: Record<string, any> = {}
    const submitFieldsModel: string[] = this.props.submitFieldsModel ?? Object.keys(this.props.data)
    submitFieldsModel.forEach((k: string) => {
      submitData[k] = this.props.data[k]
    })

    this.setState({submitting: true})
    api.submit(
        submitMethod,
        api.pathWithParams(submitPath, { key }),
        submitData
    ).then(res => {
      notifications.showRequestSuccess(res)
      this.setState({
        dirty: false,
        submitting: false
      }, () => this.afterSubmit())
    }).catch(err => {
      this.setState({submitting: false})
      notifications.showRequestError(err)
    })
  }

  public remove = (): void => {
    const key: CommonKey | undefined =
      this.props.entityKey !== null
      ? this.props.entityKey
      : undefined
    const deletePath: RequestApiPath | null =
      this.props.deletePath
      ?? this.props.requestPath
      ?? null;
    if (deletePath === null || key === undefined)
      return
    dialog.showConfirm({
      message: gettext("Are you sure you want to delete?"),
      captionOK: gettext("Delete"),
      colorOK: 'secondary',
      okCallback: () => {
        dialog.setBusy(true)
        api.deleteObject(deletePath, key)
          .then(res => {
            dialog.hide()
            notifications.showRequestSuccess(res)
            this.afterDelete()
          })
          .catch(err => {
            dialog.setBusy(false)
            notifications.showRequestError(err)
          })
      }
    })
  }

  public fetch = (): void => {
    if (!this.props.requestPath)
      return

    this.setState({loading: true})

    api.get(api.pathWithParams(this.props.requestPath, {key: this.props.entityKey})).then(res => {
      this.props.onFetch ? this.props.onFetch(res.data) : this.handleFetch(res.data)
    }).catch(err => {
      this.setState({
        loading: false,
        success: false
      })
      if (this.props.onError) {
        this.props.onError(err)
      } else if (this.props.onErrorShowMsg ?? true) {
        const msg: string = typeof this.props.onErrorShowMsg === 'string'
          ? this.props.onErrorShowMsg
          : this.props.entityName
            ? [
              `${gettext('An error occurred while fetching data from the server', 'system.ui-common')}`,
              this.props.entityName
            ].join(': ')
            : `${gettext('An error occurred while fetching data from the server', 'system.ui-common')}`
        notifications.showError(msg)
      }
    })
  }

  public handleFetch = (response: EntityData): void => {
    const data = this.props.data
    for (let name in response) {
      if (!response.hasOwnProperty(name))
        continue
      if (!(name in data))
        continue
      data[name] = response[name]
    }
    this.props.onUpdateData(data, () => this.setState({
      loading: false,
      success: true
    }))
  }

  private extractFieldName = (e: any): string | null => {
    return e.name || e.key || e.id || null
  }

  private handleFieldValueChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | null>): void => {
    const fieldName: string | null = this.extractFieldName(e.target)
    if (!fieldName)
      return

    const
      data: EntityData = this.props.data,
      targetElement: HTMLElement = e.target
    let value: any = undefined

    if (e.type === 'null') {
      value = null
    } else {
      if (targetElement.tagName === 'INPUT') {
        switch ((targetElement as HTMLInputElement).type) {
          case 'checkbox':
            value = Boolean((targetElement as HTMLInputElement).checked)
            break
          default:
            value = (targetElement as HTMLInputElement).value
        }
      }
    }

    if (value === undefined)
      return
    data[fieldName] = value
    this.props.onUpdateData(data)
  }

  private elementsFrom = (elements: any | any[]): any[] => {
    if (elements === null || elements === undefined)
      return elements
    if (Array.isArray(elements))
      return elements
    return [elements]
  }

  private makeChildren = (elements: ReactElements): ReactElements => {
    if (elements === null || elements === undefined)
      return elements

    const results: ReactElements = React.Children.map(this.elementsFrom(elements), (child: any) => {
      if (typeof child != 'object' || child === null || child === undefined)
        return child
      const childElement = child as Record<string, any>
      const childProps = Object.assign({}, childElement.props)
      if (childProps === undefined)
        return child

      const children: ReactElements = childProps.children !== undefined
        ? this.makeChildren(childProps.children)
        : undefined

      const propControl: ReactElements = childProps.control !== undefined
        ? this.makeChildren(childProps.control)
        : undefined
      if (propControl) {
        childProps['control'] = propControl
      }

      const name: string | null = this.extractFieldName(childProps)
      if (name && (String(name) in this.props.data)) {
        if (childProps['onChange'] === undefined) {
          childProps['onChange'] = this.handleFieldValueChange
        }
      }

      const component = React.cloneElement(
        child,
        childProps,
        children
      )
      // component.key = childProps['key']
      return component
    })

    return results.length === 1 ? results[0] : results
  }

  private requiredIsSatisfying = (): boolean => {
    if (this.props.requiredForSubmit === undefined || !this.props.requiredForSubmit.length)
      return true
    for (let i = 0; i < this.props.requiredForSubmit.length; i++) {
      const name: string = this.props.requiredForSubmit[i]
      const value: any = this.props.data[name]
      if (value === '' || value === undefined || value === null)
        return false
    }
    return true
  }

  render() {
    if (this.state.loading)
      return (
        <LoadingLinear />
      )

    if (!this.state.success)
      return null

    const requiredForSubmit: string[] = this.props.requiredForSubmit ?? []
    const variantOutlined: boolean = ((this.props.variant ?? 'embedded') === 'outlined')

    const Contents = (
      <Box
        p={variantOutlined ? 2 : 0}
        mt={1}
        style={{
          borderRadius: variantOutlined ? '7px' : undefined,
          backgroundColor: variantOutlined ? '#f1f1f1' : undefined,
          border: variantOutlined ? '1px solid #e5e5e5' : undefined
        }}
      >
        {this.makeChildren(this.props.children)}
      </Box>
    )

    const Controls = (
      <React.Fragment>
      {(this.props.close ?? true) && (
        <Box>
          <Button
            color={'primary'}
            onClick={this.close}
            // variant={'outlined'}
            startIcon={<BackIcon />}
            // size={this.props.windowed ? 'small' : undefined}
          >{
            (typeof this.props.close == 'string')
              ? String(this.props.close)
              : this.props.windowed
                ? gettext("Close")
                : gettext("Back")
          }</Button>
        </Box>
      )}
      <Box>
        {(this.props.delete ?? false) && (
          <Box>
            <Tooltip title={gettext("Delete")}>
              <Button
                color={'secondary'}
                onClick={this.remove}
                // variant={'outlined'}
              ><DeleteIcon /* fontSize={this.props.windowed ? 'small' : undefined} */ /></Button>
            </Tooltip>
          </Box>
        )}
      </Box>
      {(this.props.submit ?? false) && (
        <Box>
          <Button
            color={'primary'}
            disabled={
              (this.props.submitDisabled ?? false)
              || (requiredForSubmit.length === 0 || (!this.requiredIsSatisfying()))
            }
            onClick={this.submit}
            // variant={'contained'}
            variant={'outlined'}
            // size={this.props.windowed ? 'small' : undefined}
            startIcon={this.state.submitting ? <CircularProgress size={20} /> : <SubmitIcon />}
          >{(typeof this.props.submit == 'string') ? String(this.props.submit) : gettext("Save")}</Button>
        </Box>
      )}
      </React.Fragment>
    )

    const ControlsBar = this.props.windowed
      ? (
        <DialogActions>
          {Controls}
        </DialogActions>
      )
      : (
        <Toolbar style={{
          backgroundColor: '#f7f7f7',
          justifyContent: 'space-between',
          padding: '0 16px',
          margin: '0 -16px',
          top: 0,
          position: 'sticky',
          borderBottom: '1px solid #ccc',
          zIndex: 100
        }}>
          {Controls}
        </Toolbar>
      )

    return (
      <React.Fragment>
        {(this.props.windowed ?? false) ? (
          <React.Fragment>
            {Boolean(this.props.title) && (
              <DialogTitle style={{
                backgroundColor: '#eee',
                borderBottom: '1px solid #e0e0e0'
              }}>
                <Typography color={'primary'}>{this.props.title}</Typography>
              </DialogTitle>
            )}
            <DialogContent>
              {Contents}
            </DialogContent>
            {ControlsBar}
          </React.Fragment>
        ) : (
          <React.Fragment>
            {ControlsBar}
            {Contents}
          </React.Fragment>
        )}
        <Backdrop open={this.state.submitting} style={{
          position: 'fixed',
          left: 0,
          top: 0,
          right: 0,
          bottom: 0,
          zIndex: 65535,
          backgroundColor: '#ffffff11'
        }} />
      </React.Fragment>
    )
  }
}
