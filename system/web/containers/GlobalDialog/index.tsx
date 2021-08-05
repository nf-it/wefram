import React from 'react'
import {observer} from 'mobx-react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  CircularProgress, Button
} from '@material-ui/core'
import {IDialog, DialogButton} from '../../dialog'


export type GlobalDialogProps = {
  store: IDialog
}


class _Dialog extends React.Component<GlobalDialogProps> {
  render() {
    return (
      <Dialog open={this.props.store.open} onClose={!this.props.store.busy ? this.props.store.closeCallback : undefined}>
        {this.props.store.title !== undefined && this.props.store.title !== '' && (
          <DialogTitle>{this.props.store.title}</DialogTitle>
        )}
        {this.props.store.content !== undefined && (
          <DialogContent>
            {typeof this.props.store.content == 'string' ? (
              <DialogContentText>{this.props.store.content}</DialogContentText>
            ) : this.props.store.content}
          </DialogContent>
        )}
        {this.props.store.buttons !== undefined && (
          <DialogActions>
            <CircularProgress size={20} hidden={!this.props.store.busy}/>
            {this.props.store.buttons.map((button: DialogButton) => (
              <Button
                autoFocus={button.autoFocus}
                onClick={button.onClick}
                color={button.color}
                disabled={this.props.store.busy}
                variant={button.variant}
              >{button.caption}</Button>
            ))}
          </DialogActions>
        )}
      </Dialog>
    )
  }
}


export const GlobalDialog = observer(_Dialog)
