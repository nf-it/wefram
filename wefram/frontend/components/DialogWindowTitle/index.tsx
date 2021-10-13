import React from 'react'
import {gettext} from 'system/l10n'
import {Button, Box, DialogTitle, IconButton, Typography} from 'system/components'
import WindowCloseIcon from '@mui/icons-material/Cancel'
import HelpIcon from '@mui/icons-material/HelpCenterOutlined'


export type DialogWindowTitleProps = {
  title: string
  onClose: () => void
  onHelp?: () => void
}


export const DialogWindowTitle = (props: DialogWindowTitleProps) => (
  <DialogTitle style={{
    borderBottom: '1px solid #f3f3f3'
  }}>
    <Box display={'flex'} alignItems={'center'}>
      <IconButton size={'small'} style={{marginRight: '16px'}} onClick={props.onClose}>
        <WindowCloseIcon style={{
          color: '#c52', width: '20px', height: '20px'
        }} />
      </IconButton>
      <Typography color={'primary'} style={{flexGrow: 1}}>{props.title}</Typography>
      {props.onHelp !== undefined && (
        <Button
          onClick={props.onHelp}
          variant={'outlined'}
          style={{fontSize: '.75em', padding: '6px 16px', color: '#181', borderColor: '#181'}}
          startIcon={<HelpIcon fontSize={'small'} style={{color: '#181'}} />}
        >
          {gettext("Help")}
        </Button>
      )}
    </Box>
  </DialogTitle>
)
