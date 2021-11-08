import React from 'react'
import {Box, FormItem, FormItemProps, Typography, DividerRuler} from 'system/components'
import {Variant} from '@mui/material/styles/createTypography'
import {FormFieldCommon} from './types'


export type FormTitleProps = FormFieldCommon & {
  color?: 'primary' | 'secondary' | 'default'
  dense?: boolean
  title: string
  variant?: Variant
}

export type FormTitleFieldProps = FormTitleProps & FormItemProps & {
  ref?: React.LegacyRef<FormTitle>
  fieldStyle?: React.CSSProperties
}


export class FormTitle extends React.Component<FormTitleProps> {

  render() {
    return (
      <Box
        mt={this.props.dense ? 1 : 3}
        mb={this.props.dense ? 0 : 2}
      >
        <Typography
          color={this.props.color}
          variant={this.props.variant ?? 'h4'}
          gutterBottom
        >
          {this.props.title}
        </Typography>
        <DividerRuler vspace={this.props.dense ? 1 : 2} />
      </Box>
    )
  }

}


export class FormTitleField extends React.Component<FormTitleFieldProps> {

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
      pt,
      pb,
      pl,
      pr,
      p,
      align,
      justify,
      width: width ?? 12,
      style: fieldStyle
    }
    return (
      <FormItem {...formItemProps}>
        <FormTitle {...elementProps} />
      </FormItem>
    )
  }

}
