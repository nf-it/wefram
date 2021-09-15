import React from 'react'
import {RouteComponentProps} from 'react-router-dom'
import {Permissions} from '../aaa'


export interface IScreen {
  name: string
  rootComponent?: React.LazyExoticComponent<any> | null
  rootComponentPath?: string | null
  requires: Permissions
  routeUrl: string
  routeParams: string[]
  params: Record<string, any>
  urlStoredState?: Record<string, string>
}

export interface IScreenRuntime {
  caption: string
}

export type IScreenRuntimes = Record<string, IScreenRuntime>

export interface ScreenProps extends RouteComponentProps, IScreen {
}

export type ScreensSchema = Record<string, IScreen>
