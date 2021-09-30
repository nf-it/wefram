import React from 'react'
import {MouseEventHandler} from 'react'
import {makeObservable, observable} from 'mobx'
import {Box, DialogContentText, TextField, Typography} from 'system/components'
import {gettext} from './l10n'


type Color = 'error' | 'inherit' | 'primary' | 'secondary' | 'success' | 'info' | 'warning' | undefined


export type DialogButton = {
  caption: string
  autoFocus: boolean
  color: Color
  variant: 'text' | 'outlined' | 'contained'
  onClick: MouseEventHandler
}


class _Store {
  open: boolean = false
  title?: string = undefined
  content?: JSX.Element | JSX.Element[] | string = undefined
  buttons?: DialogButton[] = undefined
  closeCallback?: any = undefined
  busy?: boolean = false
  inputValue?: string = ''

  constructor() {
    makeObservable(this, {
      open: observable,
      title: observable,
      content: observable,
      buttons: observable,
      closeCallback: observable,
      busy: observable,
      inputValue: observable
    })
  }
}

export const dialogsStore = new _Store()

type DialogInterface = {
  show(
      content: JSX.Element | JSX.Element[],
      title?: string,
      buttons?: DialogButton[],
      closeCallback?: any
  ): void
  showMessage(message: string, title?: string, captionOK?: string, closeCallback?: any): void
  showConfirm({
      message, title, captionOK, captionCancel, okCallback, cancelCallback, defaultOK,
      highlightOK, highlightCancel, colorOK, colorCancel
    }: {
      message?: string, title?: string, captionOK?: string, captionCancel?: string,
      okCallback?: any, cancelCallback?: any, defaultOK?: boolean,
      highlightOK?: boolean, highlightCancel?: boolean, colorOK?: Color,
      colorCancel?: Color
    }): void
  prompt({
    defaultValue, message, title, captionOK, captionCancel, okCallback, cancelCallback
  }: {
    defaultValue?: string, message?: string, title?: string, captionOK?: string,
    captionCancel?: string,
    okCallback: (value: string) => void,
    cancelCallback?: () => void
  }): void
  hide(): void
  setBusy(state: boolean): void
}

export const dialog: DialogInterface = {
  show(
      content: JSX.Element | JSX.Element[],
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
      highlightOK?: boolean, highlightCancel?: boolean, colorOK?: Color,
      colorCancel?: Color
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

export interface IDialog {
  open: boolean
  title?: string
  content?: JSX.Element | JSX.Element[] | string
  buttons?: DialogButton[]
  closeCallback?: any
  busy?: boolean
}
