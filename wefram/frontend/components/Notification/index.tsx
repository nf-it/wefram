import React from 'react'
import {
  Alert,
  AlertColor,
  Snackbar
} from 'system/components'


export type NotificationVariant = AlertColor

export type NotificationPosition = {
  vertical?: 'bottom' | 'top'
  horizontal?: 'center' | 'right' | 'left'
}

export type NotificationProps = {
  anchorOrigin?: NotificationPosition
  open: boolean
  message: string
  variant: NotificationVariant
  onClose: () => void
}


export class Notification extends React.Component<NotificationProps> {
  render() {
    const anchorOrigin = {
      vertical: this.props.anchorOrigin?.vertical ?? 'bottom',
      horizontal: this.props.anchorOrigin?.horizontal ?? 'left'
    }
    return (
      <Snackbar
        anchorOrigin={anchorOrigin}
        open={this.props.open}
        autoHideDuration={6000}
        onClose={this.props.onClose}
      >
        <Alert
          onClose={this.props.onClose}
          severity={this.props.variant}
          variant={'filled'}
          sx={{
            minWidth: '22vw',
            boxShadow: '0 5px 15px #000b'
          }}
        >
          {this.props.message}
        </Alert>
      </Snackbar>
    )
  }
}

