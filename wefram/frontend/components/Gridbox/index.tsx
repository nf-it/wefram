import React from 'react'
import {Box, BoxProps} from 'system/components'


export type GridboxProps = BoxProps & {
  autoHeight?: boolean
  columns?: number | string
  gap?: number | string
  rowGap?: number | string
  columnGap?: number | string
}


export const Gridbox = (props: GridboxProps) => {
  const {
    display,
    columns,
    autoHeight,
    gap,
    rowGap,
    columnGap,
    width,
    ...other
  } = props

  const style: any = {}

  style.display = 'grid'
  style.gridTemplateColumns = columns
    ? (typeof columns == 'number' ? `repeat(${columns}, 1fr)` : String(columns))
    : undefined
  style.gap = typeof gap == 'number'
    ? `${gap * 8}px`
    : typeof gap == 'string'
      ? gap
      : undefined
  style.rowGap = rowGap ? (
    typeof rowGap == 'number'
      ? `${rowGap * 8}px`
      : rowGap
    ) : undefined
  style.columnGap = columnGap ? (
    typeof columnGap == 'number'
      ? `${columnGap * 8}px`
      : columnGap
    ) : undefined
  style.gridAutoRows = autoHeight ? '1fr' : undefined
  style.width = String(width ?? '100%')

  return (
    <Box
      sx={style}
      {...other}
    >
      {props.children}
    </Box>
  )
}
