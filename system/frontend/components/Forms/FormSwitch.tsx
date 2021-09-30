import React from 'react'
import {FormItem, FormItemProps, FormControlLabel, Switch, SwitchProps} from 'system/components'
import {FormFieldCommon} from './types'


export type FormSwitchProps = FormFieldCommon & SwitchProps & {
  label?: string
}

export type FormSwitchFieldProps = FormSwitchProps & FormItemProps & {
  ref?: React.LegacyRef<FormSwitch>
  fieldStyle?: React.CSSProperties
}


export class FormSwitch extends React.Component<FormSwitchProps> {
  private handleOnChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    if (!this.props._formOnChange || !this.props.formName)
      return
    this.props._formOnChange(this.props.formName, e.target.checked)
  }

  render() {
    let {
      _formData,
      _formOnChange,
      formName,
      label,
      defaultChecked,  // we defaults the defaultValue to the corresponding _formData
      ...elementProps
    } = this.props
    elementProps.onChange = elementProps.onChange ?? this.handleOnChange

    return label ? (
      <FormControlLabel control={
        <Switch
          defaultChecked={
            defaultChecked ?? (
              (this.props._formData !== undefined && this.props.formName !== undefined)
                ? Boolean(this.props._formData[this.props.formName])
                : undefined
            )
          }
          {...elementProps}
        />
      } label={label} />
    ) : (
      <Switch
        defaultChecked={
          defaultChecked ?? (
            (this.props._formData !== undefined && this.props.formName !== undefined)
              ? Boolean(this.props._formData[this.props.formName])
              : undefined
          )
        }
        {...elementProps}
      />
    )
  }
}


export class FormSwitchField extends React.Component<FormSwitchFieldProps> {
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
    formItemProps.align = formItemProps.align ?? 'center'
    return (
      <FormItem {...formItemProps} >
        <FormSwitch {...elementProps} />
      </FormItem>
    )
  }
}
