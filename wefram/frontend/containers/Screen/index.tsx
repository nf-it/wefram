import React from 'react'
import {api} from 'system/api'
import {Box} from 'system/components'
import {LoadingLinear} from 'system/components'
import {notifications} from 'system/notification'
import {projectProvider} from 'system/provider'
import {ScreenProps, ScreenClass} from 'system/types'


type State = {
  prerenderSuccess: boolean
}

export class Screen extends React.Component<ScreenProps, State> {
  state: State = {
    prerenderSuccess: false
  }

  componentDidMount() {
    const screenClass: ScreenClass = this.props.screenClass
    if (screenClass === 'ManagedScreen') {
      this.managedScreenPrerender()
    }
  }

  private managedScreenPrerender = (): void => {
    projectProvider.prerenderManagedScreen(this.props.name).then(res => {
      this.setState({
        prerenderSuccess: true
      })
    }).catch(err => {
      notifications.showRequestError(err)
    })
  }

  render() {
    const RootComponent: any | null = this.props.rootComponent || null
    const screenClass: ScreenClass = this.props.screenClass

    if (screenClass === 'ManagedScreen' && !this.state.prerenderSuccess) {
      return (
        <LoadingLinear />
      )
    }

    return (
      <React.Fragment>
        {RootComponent !== null && (
          <React.Suspense fallback={<LoadingLinear open={true}/>}>
            <Box className={`Screen-${this.props.name}`}>
              <RootComponent {...this.props} />
            </Box>
          </React.Suspense>
        )}
      </React.Fragment>
    )
  }
}
