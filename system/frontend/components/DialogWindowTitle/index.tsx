import React from 'react'
import {Box, DialogTitle, Typography} from 'system/components'
import {IconButton} from '@material-ui/core'
import WindowCloseIcon from '@material-ui/icons/Cancel'


export type DialogWindowTitleProps = {
  title: string
  onClose: () => void
}


export class DialogWindowTitle extends React.Component<DialogWindowTitleProps> {
  render() {
    return (
      <DialogTitle style={{
        borderBottom: '1px solid #f3f3f3'
      }}>
        <Box display={'flex'} alignItems={'center'}>
          <IconButton size={'small'} style={{marginRight: '16px'}} onClick={this.props.onClose}>
            <WindowCloseIcon style={{
              color: '#c52', width: '20px', height: '20px'
            }} />
          </IconButton>
          <Typography color={'primary'} style={{flexGrow: 1}}>{this.props.title}</Typography>
        </Box>
      </DialogTitle>
    )
  }
}