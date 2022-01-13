import React from 'react'
import {FormItem, FormItemProps, DatePicker, DatePickerProps} from 'system/components'
import {isValidDate} from 'system/tools'
import {FormFieldCommon} from './types'


export type FormDatePickerProps = FormFieldCommon & DatePickerProps & {
  inputType?: string
  dense?: boolean
  small?: boolean
}

export type FormDatePickerFieldProps = FormDatePickerProps & FormItemProps & {
  ref?: React.LegacyRef<FormDatePicker>
  fieldStyle?: React.CSSProperties
}


export class FormDatePicker extends React.Component<FormDatePickerProps> {

  private handleOnChange = (value: Date | null): void => {
    if (!this.props._formOnChange || !this.props.formName)
      return
    let val: string | null
    try {
      val = isValidDate(value) && value !== null ? value.toISOString().split('T')[0] : null
    } catch (e) {
      val = null
    }
    this.props._formOnChange(this.props.formName, val)
  }

  render() {
    let {
      _formData,
      _formOnChange,
      formName,
      defaultValue,  // we defaults the defaultValue to the corresponding _formData
      dense,  // simplificates dense from 'margin=dense' to boolean 'dense'
      inputType,  // simplicates the 'type' attribute of the <input> element
      fullWidth,  // we overrides fullWidth defaults in forms from 'false' to 'true'
      small,
      ...elementProps
    } = this.props

    elementProps.onChange = elementProps.onChange ?? this.handleOnChange
    elementProps.margin = elementProps.margin ?? ((dense ?? true) ? 'dense' : 'normal')

    return (
      <DatePicker
        defaultValue={
          defaultValue ?? (
            (this.props._formData !== undefined && this.props.formName !== undefined)
              ? this.props._formData[this.props.formName]
              : ''
          )
        }
        size={small ? 'small' : 'medium'}
        fullWidth={fullWidth ?? true}
        {...elementProps}
      />
    )
  }

}


export class FormDatePickerField extends React.Component<FormDatePickerFieldProps> {

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
        <FormDatePicker {...elementProps} />
      </FormItem>
    )
  }

}
