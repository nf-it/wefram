import React from 'react'
import {Box, Grid, GridSize, Typography} from 'system/components'


export type FormItemProps = {
  width?: GridSize
  pt?: number
  pb?: number
  pl?: number
  pr?: number
  p?: number
  align?: 'default' | 'top' | 'center' | 'bottom'
  justify?: 'default' | 'begin' | 'center' | 'end' | 'space-between' | 'space-around'
  caption?: string
  captionPosition?: 'top' | 'bottom'
  style?: React.CSSProperties
  fieldInnerStyle?: React.CSSProperties
}


export class FormItem extends React.Component<FormItemProps> {
  render() {
    let align = undefined
    switch (this.props.align) {
      case 'top':
        align = 'flex-start'
        break
      case 'bottom':
        align = 'flex-end'
        break
      case 'center':
        align = 'center'
        break
    }

    let justify = undefined
    switch (this.props.justify) {
      case 'begin':
        justify = 'flex-start'
        break
      case 'end':
        justify = 'flex-end'
        break
      case 'center':
        justify = 'center'
        break
      case 'space-between':
        justify = 'space-between'
        break
      case 'space-around':
        justify = 'space-around'
        break
    }

    const style: React.CSSProperties = this.props.style ?? {}
    style.paddingTop = this.props.pt !== undefined
      ? `${this.props.pt * 8}`
      : this.props.p !== undefined
        ? `${this.props.p * 8}`
        : style.paddingTop
    style.paddingBottom = this.props.pb !== undefined
      ? `${this.props.pb * 8}`
      : this.props.p !== undefined
        ? `${this.props.p * 8}`
        : style.paddingBottom
    style.paddingLeft = this.props.pl !== undefined
      ? `${this.props.pl * 8}`
      : this.props.p !== undefined
        ? `${this.props.p * 8}`
        : style.paddingLeft
    style.paddingRight = this.props.pr !== undefined
      ? `${this.props.pr * 8}`
      : this.props.p !== undefined
        ? `${this.props.p * 8}`
        : style.paddingRight

    const innerStyle = this.props.fieldInnerStyle ?? {}
    if ((this.props.align ?? 'default') !== 'default' || (this.props.justify ?? 'default') !== 'default') {
      innerStyle.display = style.display ?? 'flex'
      style.display = style.display ?? 'flex'
      style.flexFlow = 'column'
    }
    innerStyle.alignItems = style.alignItems ?? align
    innerStyle.justifyContent = style.justifyContent ?? justify
    innerStyle.width = innerStyle.width ?? '100%'
    innerStyle.height = innerStyle.height ?? '100%'

    return (
      <Grid item xs={this.props.width ?? 'auto'} style={style}>
        {this.props.caption !== undefined && (this.props.captionPosition ?? 'top') === 'top' && (
          <Box>
            <Typography variant={'subtitle2'}>{this.props.caption}</Typography>
          </Box>
        )}
        <Box style={innerStyle}>
          {this.props.children}
        </Box>
        {this.props.caption !== undefined && (this.props.captionPosition ?? 'top') === 'bottom' && (
          <Box>
            <Typography variant={'subtitle2'}>{this.props.caption}</Typography>
          </Box>
        )}
      </Grid>
    )
  }
}
