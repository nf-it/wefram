import React from 'react'
import {RouteComponentProps} from 'react-router-dom'
import {Permissions} from '../aaa'


export type ScreenClass = 'Screen' | 'ManagedScreen' | 'CompositeScreen'

export type ScreenModelProps = {
  app: string
  name: string
  screenClass: ScreenClass
  rootComponent?: React.LazyExoticComponent<any> | null
  rootComponentPath?: string | null
  requires: Permissions
  routeUrl: string
  routeParams: string[]
  params: Record<string, any>
  urlStoredState?: Record<string, string>
}

export type ScreenConfiguration = {
  caption: string
}

export type ScreensConfiguration = Record<string, ScreenConfiguration>

export type ScreenProps = RouteComponentProps & ScreenModelProps

export type ManagedScreenProps = ScreenProps & {
  managedProps?: any
}

export type ScreensSchema = Record<string, ScreenModelProps>
