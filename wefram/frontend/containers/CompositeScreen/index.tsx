import React from 'react'
import {ScreenProps} from 'system/screens'


type ScreenStateAny = Record<string, any>

type ScreenState = ScreenStateAny & { }


export class CompositeScreen extends React.Component<ScreenProps, ScreenState> {
  render() {
    return null
  }
}
