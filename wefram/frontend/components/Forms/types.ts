import React from 'react'
import {RequestApiPath, RequestMethod} from 'system/routing'
import {Permissions} from 'system/aaa'
import {ApiEntityComplexResponse, ApiEntityResponse} from 'system/types'


export type FormFieldCommon = {
  _formData?: any
  _formOnChange?: (name: string, newValue: any) => void
  formName?: string
}


export type EntityFormProps = {
  close?: string | boolean
  closeOnSubmit?: boolean
  confirmOnUnsaved?: boolean
  controls?: React.ReactNode
  data: any
  dataInitial?: any
  delete?: string | boolean
  deleteDisabled?: boolean
  deletePath?: RequestApiPath | string
  deleteMethod?: RequestMethod
  deleteRequres?: Permissions
  entityName?: string
  entityKey?: string | null
  help?: React.ReactNode
  stateDataName?: string
  requestDeep?: boolean
  requestPath?: RequestApiPath | string
  requiredForSubmit?: string[]
  skipUnsavedAttrsWarn?: string[]
  submit?: string | boolean
  submitDisabled?: boolean
  submitPath?: RequestApiPath | string
  submitMethod?: RequestMethod
  submitRequres?: Permissions
  submitFieldsModel?: string[]
  title?: string
  variant?: 'outlined' | 'embedded'
  warnOnUnsaved?: boolean | string[]
  windowed?: boolean

  /** Calls after API->delete succeed, but before form closed **/
  onAfterDelete?: () => void
  /** Calls after fetch done and loaded data being set up **/
  onAfterFetch?: () => void
  /** Calls after successful submit, but before form closed **/
  onAfterSubmit?: () => void
  /** Calls on every controlled field value change **/
  onChange?: (fieldName: string, newValue: any) => void
  /** Calls when form about to be closed to close the form from host component **/
  onClose?: () => void
  /** Calls on initial data (fetched) needs to be set up (EntityForm cannot set up data itself **/
  onInitiateData?: (data: any, cb?: any) => void
  /** Calls on every controlled field value change, giving entire data with updated value too **/
  onUpdateData?: (data: any, cb?: any) => void
  /** Calls on error occured **/
  onError?: (err: any) => void
  /** The error message (string) or default message (if true); error will not be shown on false **/
  onErrorShowMsg?: boolean | string
  /** Calls on fetch done, overriding the default EntityForm fetched data handling at all **/
  onFetch?: (response: ApiEntityResponse | ApiEntityComplexResponse) => void
  /** Calls on fetch done, but before initial data to be set up; useful to handle fetched data **/
  onFetchMakeData?: (data: any) => any
}
