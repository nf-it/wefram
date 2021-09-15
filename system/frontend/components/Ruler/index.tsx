import React from 'react'
import {withTheme, WithTheme} from '@material-ui/core'
import {Box} from 'system/components'


export interface RulerProps extends WithTheme {
  width?: 'sm' | 'md' | 'lg' | 'xl' | number
  vspace?: number
  hspace?: number
}


export class _Ruler extends React.Component<RulerProps> {
  render() {
    let width: undefined | string = undefined
    if (this.props.width) {
      let widthPx: number
      switch (this.props.width) {
        case 'sm':
          widthPx = Number(this.props.theme.breakpoints.values.sm)
          break
        case 'md':
          widthPx = Number(this.props.theme.breakpoints.values.md)
          break
        case 'lg':
          widthPx = Number(this.props.theme.breakpoints.values.lg)
          break
        case 'xl':
          widthPx = Number(this.props.theme.breakpoints.values.xl)
          break
        default:
          widthPx = Number(this.props.width)
      }
      width = `${widthPx}px`
    }
    return (
      <Box
        minWidth={width}
        width={this.props.width ? '100%' : undefined}
        mt={this.props.vspace}
        ml={this.props.hspace}
      />
    )
  }
}

export const Ruler = withTheme(_Ruler)
