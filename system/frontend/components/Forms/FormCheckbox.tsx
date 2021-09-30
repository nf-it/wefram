import React from 'react'
import {FormItem, FormItemProps, FormControlLabel, Checkbox, CheckboxProps} from 'system/components'
import {FormFieldCommon} from './types'


export type FormCheckboxProps = FormFieldCommon & CheckboxProps & {
  label?: string
}

export type FormCheckboxFieldProps = FormCheckboxProps & FormItemProps & {
  ref?: React.LegacyRef<FormCheckbox>
  fieldStyle?: React.CSSProperties
}


export class FormCheckbox extends React.Component<FormCheckboxProps> {
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
        <Checkbox
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
      <Checkbox
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


export class FormCheckboxField extends React.Component<FormCheckboxFieldProps> {
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
        <FormCheckbox {...elementProps} />
      </FormItem>
    )
  }
}
