/**
 * Provides common dialog facility. Both custom dialogs and most commonly
 * used predefined are provided here.
 *
 * The dialog is a modal interface window, which usually renders the some
 * textual contents and some actions (at least - the "Close" button). The
 * most common cases are some kind of notification or warning, and the
 * confirmation dialog (Yes-No variant).
 */

import React from 'react'
import {MouseEventHandler} from 'react'
import {makeObservable, observable} from 'mobx'
import {Box, DialogContentText, TextField, Typography} from 'system/components'
import {gettext} from './l10n'


type Color =
  | 'error'
  | 'inherit'
  | 'primary'
  | 'secondary'
  | 'success'
  | 'info'
  | 'warning'
  | undefined


/**
 * The dialog button type, used to declare dialog buttons.
 */
export type DialogButton = {
  /** The button caption */
  caption: string
  /** Set to `true` to set the focus to this button on the dialog open */
  autoFocus: boolean
  /** The button's color: the MUi's <Button> color prop */
  color: Color
  /** The button's variant: the MUI's <Button> variant prop */
  variant: 'text' | 'outlined' | 'contained'
  /** The callback for the button click action */
  onClick: MouseEventHandler
}


/**
 * The MobX store type for the dialog global state.
 */
class Store {
  /** Sets to `true` to open the dialog modal */
  open: boolean = false
  /** The dialog's window's title */
  title?: string = undefined
  /** The dialog's content - the JSX elements */
  content?: React.ReactNode
  /** The array of dialog window buttons of type {DialogButton} */
  buttons?: DialogButton[] = undefined
  /** The callback fires on the dialog close */
  closeCallback?: any = undefined
  /** If set to `true` - the busy indicator will be rendered for the dialog, while set to `true`. */
  busy?: boolean = false
  /** Used for controlled dialog's input value */
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

/**
 * The MobX store for the dialog global state.
 */
export const dialogsStore = new Store()

/**
 * Dialog project interface.
 */
type DialogInterface = {

  /**
   * Shows the modal dialog with given contents, title, buttons, etc.
   * @param content - the React node(s) for the content.
   * @param title - the dialog window's title.
   * @param buttons - button(s) of type {DialogButton} of the dialog window.
   * @param closeCallback - the callback fired on the dialog close.
   */
  show(
      content: React.ReactNode,
      title?: string,
      buttons?: DialogButton[],
      closeCallback?: any
  ): void

  /**
   * The common case to show the dialog with some text and the single "OK" button.
   * @param message - the text message to show.
   * @param title - the title of the message (of the dialog window).
   * @param captionOK - the caption of the "OK" button; or the default "OK" will be used by default.
   * @param closeCallback - the callback fired on the "OK" button click.
   */
  showMessage(message: string, title?: string, captionOK?: string, closeCallback?: any): void

  /**
   * The common case to show the confirmation dialog with "Ok" and "Cancel" buttons.
   * @param message - the text confirmation message to show.
   * @param title - the title of the confirmation (of the dialog window).
   * @param captionOK - the "YES" or "OK" button (or the default localized "OK" will be used instead).
   * @param captionCancel - the "Cancel" button (or the default localized "Cancel" will be used instead).
   * @param okCallback - the callback fired on the "OK" button click.
   * @param cancelCallback - the callback fires on the "Cancel" button click.
   * @param defaultOK - if set to `true` - the "OK" button will be focused on the dialog open.
   * @param highlightOK - if set to `true` - the "OK" button will be visually highlighted.
   * @param highlightCancel - if set to `true` - the "Cancel" button will be visually highlighted.
   * @param colorOK - the color of the "OK" button component.
   * @param colorCancel - the color of the "Cancel" button component.
   */
  showConfirm({
      message, title, captionOK, captionCancel, okCallback, cancelCallback, defaultOK,
      highlightOK, highlightCancel, colorOK, colorCancel
    }: {
      message?: string, title?: string, captionOK?: string, captionCancel?: string,
      okCallback?: any, cancelCallback?: any, defaultOK?: boolean,
      highlightOK?: boolean, highlightCancel?: boolean, colorOK?: Color,
      colorCancel?: Color
    }): void

  /**
   * The common case to show the string input dialog with optional text message.
   * @param defaultValue - the value to set as default input text on the dialog open.
   * @param message - the text message to be rendered above the input.
   * @param title - the dialog title.
   * @param captionOK - the "OK" button (or the default localized "OK" will be used instead).
   * @param captionCancel - the "Cancel" button (or the default localized "Cancel" will be used instead).
   * @param okCallback - the callback fired on the "OK" button click.
   * @param cancelCallback - the callback fires on the "Cancel" button click.
   */
  prompt({
    defaultValue, message, title, captionOK, captionCancel, okCallback, cancelCallback
  }: {
    defaultValue?: string,
    message?: string,
    title?: string,
    captionOK?: string,
    captionCancel?: string,
    okCallback: (value: string) => void,
    cancelCallback?: () => void
  }): void

  /** Called to hide the dialog modal. */
  hide(): void

  /**
   * Sets the dialog's busy state.
   * @param state - if set to `true` - the 'busy' indicator will be rendered on the
   * dialog window; otherwise, if set to `fasle` - it will be hidden.
   */
  setBusy(state: boolean): void
}

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

export type DialogMobxStoreType = {
  open: boolean
  title?: string
  content?: React.ReactNode
  buttons?: DialogButton[]
  closeCallback?: any
  busy?: boolean
}
