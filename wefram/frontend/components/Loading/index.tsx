import React from 'react'
import {Backdrop, CircularProgress, LinearProgress} from 'system/components'
import {observer} from 'mobx-react'


export type LoadingProps = {
  open: boolean
}

export type LoadingGlobalProps = {
  busy: boolean
}


export class Loading extends React.Component<LoadingProps> {
  render() {
    return (
      <Backdrop open={this.props.open} style={{
        zIndex: 65535,
        backgroundColor: '#ffffffa0'
      }}>
        <CircularProgress/>
      </Backdrop>
    )
  }
}


export class LoadingLinear extends React.Component<any> {
  render() {
    return (
      <div>
        <LinearProgress/>
      </div>
    )
  }
}


class _LoadingGlobal extends React.Component<LoadingGlobalProps> {
  render() {
    return (
      <Loading open={this.props.busy} />
    )
  }
}


export const LoadingGlobal = observer(_LoadingGlobal)
