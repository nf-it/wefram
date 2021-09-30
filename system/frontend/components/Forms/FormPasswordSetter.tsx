import React from 'react'
import {FormItem, FormItemProps, PasswordSetter, PasswordSetterProps} from 'system/components'
import {FormFieldCommon} from './types'


export type FormPasswordSetterProps = FormFieldCommon & PasswordSetterProps & {
  small?: boolean
}

export type FormPasswordSetterFieldProps = FormPasswordSetterProps & FormItemProps & {
  ref?: React.LegacyRef<FormPasswordSetter>
  fieldStyle?: React.CSSProperties
}


export class FormPasswordSetter extends React.Component<FormPasswordSetterProps> {

  private handleOnChange = (name: string | undefined, newValue: any): void => {
    if (!this.props._formOnChange || !this.props.formName)
      return
    this.props._formOnChange(this.props.formName, newValue)
  }

  render() {
    let {
      _formData,
      _formOnChange,
      formName,
      small,
      ...elementProps
    } = this.props
    elementProps.onChange = elementProps.onChange ?? this.handleOnChange

    return (
      <PasswordSetter
        size={small ? 'small' : 'medium'}
        {...elementProps}
      />
    )
  }

}


export class FormPasswordSetterField extends React.Component<FormPasswordSetterFieldProps> {
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
        <FormPasswordSetter {...elementProps} />
      </FormItem>
    )
  }
}
