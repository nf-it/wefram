import React from 'react'
import {Box} from '@material-ui/core'
import {LoadingLinear} from '../../components'
import {ScreenProps} from '../../types'


export class Screen extends React.Component<ScreenProps> {
  render() {
    const RootComponent: any | null = this.props.rootComponent || null
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
