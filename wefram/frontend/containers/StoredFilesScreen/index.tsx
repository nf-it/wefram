import React from 'react'
import {ScreenProps} from 'system/screens'
import {
  Box,
  Paper,
  StoredFilesList,
  Typography
} from 'system/components'
import {runtime} from 'system/project'


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
          <Typography variant={'h4'} paddingBottom={2}>{screenCaption || 'Files'}</Typography>
        </Box>
        <Paper variant={'outlined'} style={{
          paddingTop: '8px',
          paddingBottom: '8px'
        }}>
          <StoredFilesList
            apiEntity={this.props.params['apiEntity']}
            storageEntity={this.props.params['storageEntity']}
            minHeight={'calc(100vh - 72px - 16px)'}
          />
        </Paper>
      </React.Fragment>
    )
  }
}
