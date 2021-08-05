import React from 'react'
import {Backdrop, CircularProgress, LinearProgress} from '@material-ui/core'
import {observer} from 'mobx-react'
import {IRuntime} from '../../runtime'


export type LoadingProps = {
  open: boolean
}

export type LoadingGlobalProps = {
  runtime: IRuntime
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


export class LoadingCircular extends React.Component<any> {
  render() {
    return (
      <div>
        <CircularProgress/>
      </div>
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


export class _LoadingGlobal extends React.Component<LoadingGlobalProps> {
  render() {
    return (
      <Loading open={this.props.runtime.busy} />
    )
  }
}

export const LoadingGlobal = observer(_LoadingGlobal)
