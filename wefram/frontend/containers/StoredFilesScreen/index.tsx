import React from 'react'
import {ScreenProps} from 'system/types'
import {
  Box,
  StoredFilesList,
  Typography
} from 'system/components'
import {runtime} from 'system/runtime'


type ScreenState = {
  loading: boolean
}


export default class Screen extends React.Component<ScreenProps, ScreenState> {
  state: ScreenState = {
    loading: true
  }

  render() {
    const screenCaption: string = runtime.screens[this.props.name].caption
    return (
      <React.Fragment>
        <Box mt={1}>
          <Typography variant={'h4'}>{screenCaption || 'Files'}</Typography>
        </Box>
        <Box>
          <StoredFilesList
            apiEntity={this.props.params['apiEntity']}
            storageEntity={this.props.params['storageEntity']}
          />
        </Box>
      </React.Fragment>
    )
  }
}
