import React from 'react'
import {FormItem, FormItemProps, DigitsInputField, DigitsInputFieldProps} from 'system/components'
import {FormFieldCommon} from './types'


export type FormDigitsInputProps = FormFieldCommon & DigitsInputFieldProps & {
  ref?: React.LegacyRef<FormDigitsInput>
  dense?: boolean
  small?: boolean
}

export type FormDigitsInputFieldProps = FormDigitsInputProps & FormItemProps & {
  ref?: React.LegacyRef<FormDigitsInput>
  fieldStyle?: React.CSSProperties
}


export class FormDigitsInput extends React.Component<FormDigitsInputProps> {

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
      defaultValue,   // we defaults the defaultValue to the corresponding _formData
      dense,          // simplificates dense from 'margin=dense' to boolean 'dense'
      fullWidth,      // we overrides fullWidth defaults in forms from 'false' to 'true'
      small,
      ...elementProps
    } = this.props

    elementProps.onChange = elementProps.onChange ?? this.handleOnChange
    elementProps.margin = elementProps.margin ?? ((dense ?? true) ? 'dense' : 'normal')

    return (
      <DigitsInputField
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


export class FormDigitsInputField extends React.Component<FormDigitsInputFieldProps> {

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
        <FormDigitsInput {...elementProps} />
      </FormItem>
    )
  }

}
