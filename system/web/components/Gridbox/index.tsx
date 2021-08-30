import React from 'react'
import {Box, BoxProps} from '@material-ui/core'


export type GridboxProps = BoxProps & {
  autoHeight?: boolean
  columns?: number | string
  gap?: number | string
  rowGap?: number | string
  columnGap?: number | string
}


export class Gridbox extends React.Component<GridboxProps> {
  render() {
    const {
      display,
      columns,
      autoHeight,
      gap,
      rowGap,
      columnGap,
      width,
      ...other
    } = this.props

    return (
      <Box
        display={'grid'}
        gridTemplateColumns={columns ? (
          typeof columns == 'number' ? `repeat(${columns}, 1fr)` : String(columns)
        ) : undefined}
        gridGap={typeof gap == 'number'
          ? `${gap * 8}px`
          : typeof gap == 'string'
            ? gap
            : undefined
        }
        gridRowGap={rowGap ? (
          typeof rowGap == 'number'
            ? `${rowGap * 8}px`
            : rowGap
        ) : undefined}
        gridColumnGap={columnGap ? (
          typeof columnGap == 'number'
            ? `${columnGap * 8}px`
            : columnGap
        ) : undefined}
        gridAutoRows={autoHeight ? '1fr' : undefined}
        width={width ?? '100%'}
        {...other}
      >
        {this.props.children}
      </Box>
    )
  }
}
