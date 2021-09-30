import React from 'react'
import {Divider as MuiDivider, DividerProps as MuiDividerProps} from 'system/components'


export type DividerRulerProps = MuiDividerProps & {
  vspace?: number
  hspace?: number
}

export const DividerRuler = (props: DividerRulerProps) => {
  const {
      vspace, hspace, ...other
    } = props
    return (
      <MuiDivider style={{
        marginTop: vspace ? `${vspace * 8}px` : undefined,
        marginBottom: vspace ? `${vspace * 8}px` : undefined,
        marginLeft: hspace ? `${hspace * 8}px` : undefined,
        marginRight: hspace ? `${hspace * 8}px` : undefined,
      }} {...other} />
    )
}
