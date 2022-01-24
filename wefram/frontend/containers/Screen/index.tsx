import React from 'react'
import {api} from 'system/api'
import {Box} from 'system/components'
import {LoadingLinear} from 'system/components'
import {notifications} from 'system/notification'
import {projectProvider} from 'system/provider'
import {ScreenProps, ScreenClass} from 'system/types'


type State = {
  managedProps: any
}

export class Screen extends React.Component<ScreenProps, State> {
  state: State = {
    managedProps: undefined
  }

  componentDidMount() {
    const screenClass: ScreenClass = this.props.screenClass
    if (screenClass === 'ManagedScreen') {
      this.managedScreenPrerender()
    }
  }

  /** Used to preload the ManagedScreen typed screen from the backend */
  private managedScreenPrerender = (): void => {
    projectProvider.prerenderManagedScreen(this.props.name).then(res => {
      this.setState({
        managedProps: res.data
      })
    }).catch(err => {
      notifications.showRequestError(err)
    })
  }

  /** The screen render */
  render() {
    const RootComponent: any | null = this.props.rootComponent || null
    const screenClass: ScreenClass = this.props.screenClass

    // For the ManagedScreen we need to preload the data from the backend
    // prior to the screen render.
    if (screenClass === 'ManagedScreen' && this.state.managedProps === undefined) {
      return (
        <LoadingLinear />
      )
    }

    // Rendering the screen, using on-demand loading of the corresponding
    // JS code from the server.
    return (
      <React.Fragment>
        {RootComponent !== null && (
          <React.Suspense fallback={<LoadingLinear open={true}/>}>
            <Box className={`Screen-${this.props.name}`}>
              <RootComponent
                {...this.props}
                managedProps={this.state.managedProps}
              />
            </Box>
          </React.Suspense>
        )}
      </React.Fragment>
    )
  }
}
