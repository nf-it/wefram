import React from 'react'
import {FormItem, FormItemProps, TextField, TextFieldProps} from 'system/components'
import {FormFieldCommon} from './types'


export type FormTextInputProps = FormFieldCommon & TextFieldProps & {
  inputType?: string
  dense?: boolean
  small?: boolean
}

export type FormTextInputFieldProps = FormTextInputProps & FormItemProps & {
  ref?: React.LegacyRef<FormTextInput>
  fieldStyle?: React.CSSProperties
}


export class FormTextInput extends React.Component<FormTextInputProps> {

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
      defaultValue,  // we defaults the defaultValue to the corresponding _formData
      dense,  // simplificates dense from 'margin=dense' to boolean 'dense'
      inputType,  // simplicates the 'type' attribute of the <input> element
      fullWidth,  // we overrides fullWidth defaults in forms from 'false' to 'true'
      small,
      ...elementProps
    } = this.props

    elementProps.onChange = elementProps.onChange ?? this.handleOnChange
    elementProps.margin = elementProps.margin ?? ((dense ?? true) ? 'dense' : 'normal')
    elementProps.inputProps = elementProps.inputProps ?? {}
    if (inputType) {
      elementProps.inputProps.type = inputType
    }

    return (
      <TextField
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


export class FormTextInputField extends React.Component<FormTextInputFieldProps> {

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
        <FormTextInput {...elementProps} />
      </FormItem>
    )
  }

}
