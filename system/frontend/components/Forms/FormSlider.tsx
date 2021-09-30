import React from 'react'
import {Box, FormItem, FormItemProps, Slider, SliderProps, Typography} from 'system/components'
import {FormFieldCommon} from './types'


export type FormSliderProps = FormFieldCommon & SliderProps & {
  handleComittedChanges?: boolean  // default = true
}

export type FormSliderFieldProps = FormSliderProps & FormItemProps & {
  ref?: React.LegacyRef<FormSlider>
  fieldStyle?: React.CSSProperties
  label?: string
  labelBefore?: string | JSX.Element
  labelAfter?: string | JSX.Element
}


export class FormSlider extends React.Component<FormSliderProps> {
  private handleOnChange = (e: React.ChangeEvent<{}>, value: number | number[]): void => {
    if (!this.props._formOnChange || !this.props.formName)
      return
    this.props._formOnChange(this.props.formName, value)
  }

  render() {
    let {
      _formData,
      _formOnChange,
      formName,
      defaultValue,
      handleComittedChanges,
      ...elementProps
    } = this.props

    if (handleComittedChanges ?? true) {
      elementProps.onChange = (elementProps.onChange ?? this.handleOnChange) as any
    } else {
      elementProps.onChangeCommitted = (elementProps.onChangeCommitted ?? this.handleOnChange) as any
    }

    return (
      <Slider
        defaultValue={
          defaultValue ?? (
            (this.props._formData !== undefined && this.props.formName !== undefined)
              ? this.props._formData[this.props.formName]
              : ''
          )
        }
        {...elementProps}
      />
    )
  }
}


export class FormSliderField extends React.Component<FormSliderFieldProps> {
  render() {
    const {
      label,
      labelBefore,
      labelAfter,

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
      <FormItem
        caption={label}
        {...formItemProps}
      >
        <Box display={'flex'} justifyContent={'space-between'} alignItems={'center'}>
          {labelBefore !== undefined && (
            <Typography style={{
              marginRight: '16px',
              whiteSpace: 'nowrap'
            }}>{labelBefore}</Typography>
          )}
          <FormSlider {...elementProps} />
          {labelAfter !== undefined && (
            <Typography style={{
              marginLeft: '16px',
              whiteSpace: 'nowrap'
            }}>{labelAfter}</Typography>
          )}
        </Box>
      </FormItem>
    )
  }
}

