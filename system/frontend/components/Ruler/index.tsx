import React from 'react'
import {breakpoints, ThemeBreakpoints} from 'system/theme'
import {Box} from 'system/components'


export type RulerProps = {
  width?: 'sm' | 'md' | 'lg' | 'xl' | number
  vspace?: number
  hspace?: number
}


export class Ruler extends React.Component<RulerProps> {
  render() {
    let width: undefined | string = undefined
    if (this.props.width) {
      let widthPx: number
      if (typeof this.props.width == 'string') {
        widthPx = Number(breakpoints[this.props.width as keyof ThemeBreakpoints])
      } else {
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
