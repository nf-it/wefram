import React from 'react'
import {FormItem, FormItemProps, StoredImage, StoredImageProps} from 'system/components'
import {FormFieldCommon} from './types'


export type FormStoredImageProps = FormFieldCommon & StoredImageProps & {
  defaultValue?: string | null
}

export type FormStoredImageFieldProps = FormItemProps & FormStoredImageProps & {
  label?: string
  labelPosition?: 'top' | 'bottom'
  fieldStyle?: React.CSSProperties
}


export class FormStoredImage extends React.Component<FormStoredImageProps> {

  private handleOnChange = (fileId: string | null): void => {
    if (!this.props._formOnChange || !this.props.formName)
      return
    this.props._formOnChange(this.props.formName, fileId)
  }

  render() {
    let {
      _formData,
      _formOnChange,
      formName,
      defaultValue,   // we defaults the defaultValue to the corresponding _formData
      fileId,         // have to unpack `fileId` due to override it with the default value
      ...elementProps
    } = this.props
    elementProps.onChange = elementProps.onChange ?? this.handleOnChange

    const imageFileId: string | null = defaultValue ?? fileId ?? (
            (this.props._formData !== undefined && this.props.formName !== undefined)
              ? this.props._formData[this.props.formName]
              : null
          )

    return (
      <StoredImage
        fileId={imageFileId}
        {...elementProps}
      />
    )
  }

}


export class FormStoredImageField extends React.Component<FormStoredImageFieldProps> {

  render() {
    const {
      label,
      labelPosition,

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
      <FormItem {...formItemProps} caption={label} captionPosition={labelPosition}>
        <FormStoredImage {...elementProps} />
      </FormItem>
    )
  }

}
