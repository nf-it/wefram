import React from 'react'
import {
  Backdrop,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogWindowTitle,
  LoadingLinear,
  MaterialIcon,
  Ruler,
  Toolbar,
  Tooltip
} from 'system/components'
import {api} from 'system/api'
import {CommonKey, ApiSubmitMethod} from 'system/types'
import {RequestApiPath, routing} from 'system/routing'
import {notifications} from 'system/notification'
import {dialog} from 'system/dialog'
import {gettext} from 'system/l10n'
import {isArraysEqual, isEqual} from 'system/tools'
import {EntityFormProps} from './types'


type ReactElements = any | any[] | null | undefined


type EntityFormState = {
  dataInitial: any
  dirty: boolean
  helpOpen: boolean
  loading: boolean
  submitting: boolean
  success: boolean
}


export class EntityForm extends React.Component<EntityFormProps, EntityFormState> {
  state: EntityFormState = {
    dataInitial: {},
    dirty: false,
    helpOpen: false,
    loading: true,
    submitting: false,
    success: false
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

  public isDirty = (): boolean => {
    const dataCurrent: any = this.props.data
    const dataInitial: any = this.props.dataInitial ?? this.state.dataInitial ?? {}
    for (let k in dataCurrent) {
      if (!dataCurrent.hasOwnProperty(k))
        continue
      if (this.props.skipUnsavedAttrsWarn && this.props.skipUnsavedAttrsWarn.includes(k))
        continue
      if (!(k in dataInitial))
        return true
      const currentValue: any = dataCurrent[k]
      const initialValue: any = dataInitial[k]
      if (Array.isArray(currentValue) && Array.isArray(initialValue) && !isArraysEqual(currentValue, initialValue))
        return true
      if (typeof currentValue !== typeof initialValue)
        return true
      if (typeof currentValue == 'object' && typeof initialValue == 'object' && !isEqual(currentValue, initialValue))
        return true
      if (initialValue !== currentValue)
        return true
    }
    return false
  }

  public reqClose = (): void => {
    if (!this.isDirty() || !(this.props.warnOnUnsaved ?? true)) {
      this.close()
    } else {
      dialog.showConfirm({
        message: gettext('You have unsaved changes on your form. Are you sure you want to close it?', 'system.ui'),
        captionOK: gettext('Don\'t save', 'system.ui'),
        captionCancel: gettext('Cancel'),
        highlightCancel: true,
        okCallback: () => {
          this.close()
          dialog.hide()
        }
      })
    }
  }

  public close = (): void => {
    this.props.onClose !== undefined
      ? this.props.onClose()
      : (!this.props.windowed)
        ? routing.back()
        : null
  }

  private afterSubmit = (): void => {
    if (this.props.onAfterSubmit === undefined && this.props.closeOnSubmit === false)
      return
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

    const submitMethod: ApiSubmitMethod =
      ((this.props.submitMethod ?? (key ? 'PUT' : 'POST')).toUpperCase()) as ApiSubmitMethod

    if (!['PUT', 'POST'].includes(submitMethod))
      throw (`FormEntity.submit() - submit method ${submitMethod} is not supported!`)

    const submitData: Record<string, any> = {}
    const submitFieldsModel: string[] = this.props.submitFieldsModel ?? Object.keys(this.props.data)
    submitFieldsModel.forEach((k: string) => {
      submitData[k] = this.props.data[k]
    })

    this.setState({submitting: true})
    api.submit(
      submitMethod,
      api.pathWithParams(submitPath, {key}),
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

    api.get(api.pathWithParams(this.props.requestPath, {key: this.props.entityKey}), {
      params: this.props.requestDeep ? {deep: true} : undefined
    }).then(res => {
      this.props.onFetch
        ? this.setState({loading: false, success: true}, () => this.props.onFetch && this.props.onFetch(res.data))
        : this.handleFetch(res.data)
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
        this.close()
      }
    })
  }

  public handleFetch = (response: any): void => {
    let data = this.props.data
    for (let name in response) {
      if (!response.hasOwnProperty(name))
        continue
      if (!(name in data))
        continue
      data[name] = response[name]
    }
    if (this.props.onFetchMakeData) {
      data = this.props.onFetchMakeData(data)
    }

    const dataInitial: Record<string, any> = {}
    for (let k in data) {
      if (!data.hasOwnProperty(k))
        continue
      dataInitial[k] = data[k]
    }
    this.setState({dataInitial})

    if (this.props.onInitiateData) {
      this.props.onInitiateData(data, () => this.setState({
        loading: false,
        success: true
      }, () => this.props.onAfterFetch && this.props.onAfterFetch()))
    } else if (this.props.onUpdateData) {
      this.props.onUpdateData(data, () => this.setState({
        loading: false,
        success: true
      }, () => this.props.onAfterFetch && this.props.onAfterFetch()))
    } else {
      this.setState({
        loading: false,
        success: true
      }, () => this.props.onAfterFetch && this.props.onAfterFetch())
    }
  }

  private extractFieldName = (e: any): string | null => {
    return e.formName || e.name || e.key || e.id || null
  }

  private handleFieldValueChange = (
    ev: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | null> | string | null,
    valarg: any
  ): void => {
    if (ev === null)
      return

    const
      data: any = this.props.data,
      target: HTMLElement | any | null = typeof ev == 'string' ? null : ev.target

    const fieldName: string | null = typeof ev == 'string' ? ev : this.extractFieldName(target)
    if (!fieldName)
      return

    let value: any = undefined

    if (valarg === null) {
      value = null
    } else if (typeof valarg == 'object' && '$$typeof' in valarg) {
      if ('props' in valarg && 'value' in valarg.props) {
        value = valarg.props.value
      } else {
        valarg = undefined
      }
    }

    if (value === undefined) {
      if (typeof ev !== 'string' && ev.type === 'null') {
        value = null
      } else if (valarg !== undefined) {
        value = valarg
      } else if (target !== null) {
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
          switch ((target as HTMLInputElement).type) {
            case 'checkbox':
              value = Boolean((target as HTMLInputElement).checked)
              break
            default:
              value = (target as HTMLInputElement).value
          }
        } else if (target.name && target.value) {
          value = target.value
        }
      }
    }

    if (value === undefined)
      return
    data[fieldName] = value
    if (this.props.onChange) {
      this.props.onChange(fieldName, value)
    }
    if (this.props.onUpdateData) {
      this.props.onUpdateData(data)
    }
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
      const childProps: any = Object.assign({}, (child as any).props)
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
      const formName: string | undefined = childProps['formName']
      if (name && (String(name) in this.props.data)) {
        if (formName !== undefined) {
          childProps['_formData'] = this.props.data
          childProps['_formOnChange'] = this.handleFieldValueChange
        } else {
          if (childProps['onChange'] === undefined) {
            childProps['onChange'] = this.handleFieldValueChange
          }
        }
      }

      return React.cloneElement(
        child,
        childProps,
        children
      )
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
        <LoadingLinear/>
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
          borderRadius: variantOutlined ? '.5vmax' : undefined,
          backgroundColor: variantOutlined ? '#f1f1f1' : undefined,
          border: variantOutlined ? '1px solid #e5e5e5' : undefined
        }}
      >
        {this.makeChildren(this.props.children)}
      </Box>
    )

    const Controls = (
      <React.Fragment>
        {(this.props.submit ?? false) && (this.props.windowed) && (
          <Box>
            <Button
              color={'primary'}
              disabled={
                (this.props.submitDisabled ?? false) || !this.requiredIsSatisfying()
              }
              onClick={this.submit}
              variant={'outlined'}
              startIcon={
                this.state.submitting
                  ? <CircularProgress size={20}/>
                  : <MaterialIcon icon={'done'} />
              }
            >{(typeof this.props.submit == 'string') ? String(this.props.submit) : gettext("Save")}</Button>
          </Box>
        )}
        {(this.props.close ?? true) && (!this.props.windowed) && (
          <Box>
            <Button
              color={'primary'}
              onClick={this.reqClose}
              startIcon={
                this.props.windowed
                  ? <MaterialIcon icon={'cancel'} />
                  : <MaterialIcon icon={'arrow_back'} />
              }
            >{
              (typeof this.props.close == 'string')
                ? String(this.props.close)
                : this.props.entityKey === null
                  ? gettext("Cancel")
                  : this.props.windowed
                    ? gettext("Close")
                    : gettext("Back")
            }</Button>
          </Box>
        )}

        <Box display={'flex'} alignItems={'center'} justifyContent={'space-between'} gap={'4px'}>
          {this.props.controls !== undefined && this.props.controls}
          {this.props.help !== undefined && (!this.props.windowed) && (
            <Box>
              <Tooltip title={gettext("Help")}>
                <Button
                  onClick={() => this.setState({helpOpen: true})}
                  variant={'outlined'}
                  style={{
                    color: '#181',
                    borderColor: '#181'
                  }}
                >
                  <MaterialIcon icon={'help'} color={'#181'} />
                </Button>
              </Tooltip>
            </Box>
          )}
          {(this.props.delete ?? false) && (
            <Box>
              <Tooltip title={gettext("Delete")}>
                <Button
                  color={'secondary'}
                  onClick={this.remove}
                >
                  <MaterialIcon icon={'delete'} />
                </Button>
              </Tooltip>
            </Box>
          )}
        </Box>

        {(this.props.submit ?? false) && (!this.props.windowed) && (
          <Box>
            <Button
              color={'primary'}
              disabled={
                (this.props.submitDisabled ?? false) || (!this.requiredIsSatisfying())
              }
              onClick={this.submit}
              variant={'outlined'}
              startIcon={
                this.state.submitting
                  ? <CircularProgress size={20} />
                  : <MaterialIcon icon={'done'} />
              }
            >{(typeof this.props.submit == 'string') ? String(this.props.submit) : gettext("Save")}</Button>
          </Box>
        )}
        {(this.props.close ?? true) && (this.props.windowed) && (
          <Box>
            <Button
              color={'primary'}
              onClick={this.reqClose}
              startIcon={
                this.props.windowed
                  ? <MaterialIcon icon={'cancel'} />
                  : <MaterialIcon icon={'arrow_back'} />
              }
            >{
              (typeof this.props.close == 'string')
                ? String(this.props.close)
                : this.props.entityKey === null
                  ? gettext("Cancel")
                  : this.props.windowed
                    ? gettext("Close")
                    : gettext("Back")
            }</Button>
          </Box>
        )}
      </React.Fragment>
    )

    const ControlsBar = this.props.windowed
      ? (
        <DialogActions style={{
          borderTop: '1px solid #f3f3f3'
        }}>
          {Controls}
        </DialogActions>
      )
      : (
        <Toolbar style={{
          backgroundColor: '#f7f7f7',
          borderRadius: '.5vmax',
          justifyContent: 'space-between',
          padding: '0 16px',
          top: 0,
          position: 'sticky',
          borderBottom: '1px solid #f3f3f3',
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
              <DialogWindowTitle
                title={this.props.title ?? ''}
                onClose={this.reqClose}
                onHelp={this.props.help !== undefined ? () => this.setState({helpOpen: true}) : undefined}
              />
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
        {this.props.help !== undefined && (
          <Dialog open={this.state.helpOpen} maxWidth={'sm'}>
            <DialogWindowTitle title={gettext("Help")} onClose={() => this.setState({helpOpen: false})} />
            <DialogContent>
              <Ruler width={'sm'} />
              {this.state.helpOpen && (
                <Box>
                  {this.props.help}
                </Box>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => this.setState({helpOpen: false})}>{gettext("Close")}</Button>
            </DialogActions>
          </Dialog>
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
