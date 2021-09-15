import React from 'react'
import {ScreenProps} from 'system/types'
import {
  Box,
  StoredImagesList,
  Typography
} from 'system/components'
import {runtime} from 'system/runtime'


type StoredImagesState = {
  loading: boolean
}


export default class StoredImagesScreen extends React.Component<ScreenProps, StoredImagesState> {
  state: StoredImagesState = {
    loading: true
  }

  render() {
    const screenCaption: string = runtime.screens[this.props.name].caption
    return (
      <React.Fragment>
        <Box mt={2} mb={2}>
          <Typography variant={'h4'}>{screenCaption || 'Images'}</Typography>
        </Box>
        <Box>
          <StoredImagesList
            apiEntity={this.props.params['apiEntity']}
            storageEntity={this.props.params['storageEntity']}
            columns={this.props.params.columns}
            rowHeight={this.props.params.rowHeight}
            gap={this.props.params.gap}
          />
        </Box>
      </React.Fragment>
    )
  }
}
