import React from 'react'
import {Box, DialogContentText, TextField, Typography} from 'system/components'
import {gettext} from '../l10n'
import {DialogComponentColor, DialogButton, DialogInterface} from './types'
import {dialogsStore} from './mobx-store'


export const dialog: DialogInterface = {
  show(
      content: React.ReactNode,
      title?: string,
      buttons?: DialogButton[],
      closeCallback?: any
  ) {
    dialogsStore.content = content
    dialogsStore.title = title
    dialogsStore.content = content
    dialogsStore.buttons = buttons
    dialogsStore.closeCallback = closeCallback
    dialogsStore.busy = false
    dialogsStore.open = true
  },

  showMessage(message: string, title?: string, captionOK?: string, closeCallback?: any): void {
    const
      buttonCaptionOK: string = captionOK ?? gettext("OK"),
      callback: any = closeCallback ?? (() => dialog.hide())
    dialogsStore.title = title || undefined
    dialogsStore.closeCallback = callback
    dialogsStore.content = (
      <DialogContentText>{message}</DialogContentText>
    )
    dialogsStore.busy = false
    dialogsStore.buttons = [{
      autoFocus: true,
      caption: buttonCaptionOK,
      color: 'primary',
      variant: 'text',
      onClick: callback
    }]
    dialogsStore.open = true
  },

  showConfirm({
      message, title, captionOK, captionCancel, okCallback, cancelCallback, defaultOK,
      highlightOK, highlightCancel, colorOK, colorCancel
    }: {
      message?: string, title?: string, captionOK?: string, captionCancel?: string,
      okCallback?: any, cancelCallback?: any, defaultOK?: boolean,
      highlightOK?: boolean, highlightCancel?: boolean, colorOK?: DialogComponentColor,
      colorCancel?: DialogComponentColor
  }) {
    const
      buttonCaptionOK: string = captionOK ?? gettext("OK"),
      buttonCaptionCancel: string = captionCancel ?? gettext("Cancel"),
      callbackConfirm: any = okCallback,
      callbackCancel: any = cancelCallback ?? (() => dialog.hide()),
      messageBody: string = message ?? gettext("Are you sure?"),
      focusOK: boolean = defaultOK ?? false,
      focusCancel: boolean = !(defaultOK ?? false)
    dialogsStore.title = title
    dialogsStore.closeCallback = callbackCancel
    dialogsStore.content = (
      <DialogContentText>{messageBody}</DialogContentText>
    )
    dialogsStore.busy = false
    dialogsStore.buttons = [{
      autoFocus: focusCancel,
      caption: buttonCaptionCancel,
      color: colorCancel ?? 'primary',
      variant: highlightCancel ? 'outlined' : 'text',
      onClick: callbackCancel
    }, {
      autoFocus: focusOK,
      caption: buttonCaptionOK,
      color: colorOK ?? 'primary',
      variant: highlightOK ? 'outlined' : 'text',
      onClick: callbackConfirm
    }]
    dialogsStore.open = true
  },

  prompt({defaultValue, message, title, captionOK, captionCancel, okCallback, cancelCallback}) {
    const
      buttonCaptionOK: string = captionOK ?? gettext("OK"),
      buttonCaptionCancel: string = captionCancel ?? gettext("Cancel"),
      callbackConfirm: any = okCallback,
      callbackCancel: any = cancelCallback ?? (() => dialog.hide())
    const content: React.FunctionComponentElement<any>[] = []
    if (message) {
      content.push(
        <Box pt={2}><Typography>{message}</Typography></Box>
      )
    }
    content.push(
      <Box pt={2} pb={2} minWidth={'25vw'}>
        <TextField
          fullWidth
          defaultValue={defaultValue || ''}
          variant={'outlined'}
          onChange={(ev: React.ChangeEvent<HTMLInputElement>) => {
            dialogsStore.inputValue = ev.target.value
          }}
        />
      </Box>
    )
    dialogsStore.title = title
    dialogsStore.closeCallback = callbackCancel
    dialogsStore.content = content
    dialogsStore.busy = false
    dialogsStore.inputValue = defaultValue
    dialogsStore.buttons = [{
      autoFocus: false,
      caption: buttonCaptionCancel,
      color: 'primary',
      variant: 'text',
      onClick: callbackCancel
    }, {
      autoFocus: false,
      caption: buttonCaptionOK,
      color: 'primary',
      variant: 'text',
      onClick: () => {
        callbackConfirm(dialogsStore.inputValue)
      }
    }]
    dialogsStore.open = true
  },

  hide() {
    dialogsStore.open = false
  },

  setBusy(state: boolean) {
    dialogsStore.busy = state
  }
}