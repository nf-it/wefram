import React from 'react'
import {FormItem, FormItemProps, MenuItem, TextField, TextFieldProps} from 'system/components'
import {FormFieldCommon} from './types'


export type FormSelectFieldOptionsDict = Record<any, string>

export type FormSelectFieldOptionTuple = [any, string]

export type FormSelectFieldOption = {
  value: any
  caption: string
}

export type FormSelectProps = FormFieldCommon & TextFieldProps & {
  dense?: boolean
  small?: boolean
  options?: FormSelectFieldOption[] | FormSelectFieldOptionTuple[] | FormSelectFieldOptionsDict
}

export type FormSelectFieldProps = FormSelectProps & FormItemProps & {
  ref?: React.LegacyRef<FormSelect>
  fieldStyle?: React.CSSProperties
}


export class FormSelect extends React.Component<FormSelectProps> {

  private handleOnChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    if (!this.props._formOnChange || !this.props.formName)
      return
    this.props._formOnChange(this.props.formName, e.target.value)
  }

  render() {
    let {
      _formData,
      _formOnChange,
      formName,
      children,
      defaultValue,  // we defaults the defaultValue to the corresponding _formData
      dense,  // simplificates dense from 'margin=dense' to boolean 'dense'
      options,  // allows to specify options as Dict or List in addition to usage of children <MenuItem>
      fullWidth,  // we overrides fullWidth defaults in forms from 'false' to 'true'
      small,
      ...elementProps
    } = this.props
    elementProps.onChange = elementProps.onChange ?? this.handleOnChange
    elementProps.margin = elementProps.margin ?? (dense ? 'dense' : 'normal')

    let optionsEnum: FormSelectFieldOption[] | null
    if (options) {
      if (Array.isArray(options)) {
        optionsEnum = options.map(
          option =>
            Array.isArray(option)
              ? {value: option[0], caption: option[1]}
              : option
        )
      } else {
        optionsEnum = []
        for (let value in this.props.options) {
          if (!this.props.options.hasOwnProperty(value))
            continue
          const caption = options[value]
          optionsEnum.push({value, caption})
        }
        optionsEnum = optionsEnum.sort((a, b) => a.caption > b.caption ? 1 : -1)
      }
    } else {
      optionsEnum = null
    }

    return (
      <TextField
        select
        defaultValue={
          this.props.defaultValue ?? (
            (this.props._formData !== undefined && this.props.formName !== undefined)
              ? this.props._formData[this.props.formName]
              : ''
          )
        }
        size={small ? 'small' : 'medium'}
        fullWidth={this.props.fullWidth ?? true}
        {...elementProps}
      >
        {children}
        {optionsEnum !== null && optionsEnum.map(option => (
          <MenuItem value={option.value}>{option.caption}</MenuItem>
        ))}
      </TextField>
    )
  }

}


export class FormSelectField extends React.Component<FormSelectFieldProps> {

  render() {
    const {
      width,
      pt,
      pb,
      pl,
      pr,
      p,
      align,
      justify,
      fieldStyle,
      ...elementProps
    } = this.props
    const formItemProps = {
      width,
      pt,
      pb,
      pl,
      pr,
      p,
      align,
      justify,
      style: fieldStyle
    }
    return (
      <FormItem {...formItemProps}>
        <FormSelect {...elementProps} />
      </FormItem>
    )
  }

}
