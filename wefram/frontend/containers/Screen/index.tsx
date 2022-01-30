import React from 'react'
import {Box, Button, LoadingLinear, Typography} from 'system/components'
import {gettext} from 'system/l10n'
import {notifications} from 'system/notification'
import {projectProvider} from 'system/project'
import {ScreenProps, ScreenClass} from 'system/screens'


export type ScreenOnDemandErrorBoundaryProps = {
  children: React.ReactNode
}

type ScreenOnDemandErrorBoundaryState = {
  hasError: boolean
}

class ScreenOnDemandErrorBoundary extends React.Component<ScreenOnDemandErrorBoundaryProps, ScreenOnDemandErrorBoundaryState> {
  state: ScreenOnDemandErrorBoundaryState = {
    hasError: false
  }

  public static getDerivedStateFromError(_: Error): ScreenOnDemandErrorBoundaryState {
    return { hasError: true }
  }

  public componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box style={{
          margin: '4px 0 16px',
          padding: '32px',
          textAlign: 'center',
          border: '2px solid #d20',
          borderRadius: '4px'
        }}>
          <Typography style={{
            color: 'red',
            paddingBottom: '32px'
          }}>
            {gettext("Network error occured! Please check the internet connection and try again a little later!", 'system.responses')}
          </Typography>
          <Box style={{
            display: 'flex',
            justifyContent: 'center'
          }}>
            <Button
              variant={'outlined'}
              onClick={() => {
                window.location.reload()
              }}
            >
              {gettext("Try again", 'system.ui')}
            </Button>
          </Box>
        </Box>
      )
    }

    return this.props.children
  }
}


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
          <ScreenOnDemandErrorBoundary>
            <React.Suspense fallback={<LoadingLinear open={true}/>}>
              <Box className={`Screen-${this.props.name}`}>
                <RootComponent
                  {...this.props}
                  managedProps={this.state.managedProps}
                />
              </Box>
            </React.Suspense>
          </ScreenOnDemandErrorBoundary>
        )}
      </React.Fragment>
    )
  }
}
