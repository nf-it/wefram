import React from 'react'
import {Divider as MuiDivider, DividerProps as MuiDividerProps} from '@material-ui/core'


export type DividerRulerProps = MuiDividerProps & {
  vspace?: number
  hspace?: number
}


export class DividerRuler extends React.Component<DividerRulerProps> {
  render() {
    const {
      vspace, hspace, ...other
    } = this.props
    return (
      <MuiDivider style={{
        marginTop: vspace ? `${vspace * 8}px` : undefined,
        marginBottom: vspace ? `${vspace * 8}px` : undefined,
        marginLeft: hspace ? `${hspace * 8}px` : undefined,
        marginRight: hspace ? `${hspace * 8}px` : undefined,
      }} {...other} />
    )
  }
}
