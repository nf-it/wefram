import React from 'react'
import {
  FormItem,
  FormItemProps,
  OptionsList,
  OptionsListProps
} from 'system/components'
import {CommonKey} from 'system/types'
import {FormFieldCommon} from './types'


export type FormOptionsListProps = FormFieldCommon & OptionsListProps

export type FormOptionsListFieldProps = FormOptionsListProps & FormItemProps & {
  ref?: React.LegacyRef<FormOptionsList>
  fieldStyle?: React.CSSProperties
}


export class FormOptionsList extends React.Component<FormOptionsListProps> {
  private handleOnChange = (values: CommonKey[]): void => {
    if (!this.props._formOnChange || !this.props.formName)
      return
    this.props._formOnChange(this.props.formName, values)
  }

  render() {
    let {
      _formData,
      _formOnChange,
      formName,
      defaultValues,
      ...elementProps
    } = this.props
    elementProps.onChange = elementProps.onChange ?? this.handleOnChange

    return (
      <OptionsList
        defaultValues={
          defaultValues ?? (
            (this.props._formData !== undefined && this.props.formName !== undefined)
              ? this.props._formData[this.props.formName]
              : []
          )
        }
        {...elementProps}
      />
    )
  }
}


export class FormOptionsListField extends React.Component<FormOptionsListFieldProps> {
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
      width: width ?? 12,
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
      <FormItem {...formItemProps} >
        <FormOptionsList {...elementProps} />
      </FormItem>
    )
  }
}

