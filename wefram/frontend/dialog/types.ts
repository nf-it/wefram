import React from 'react'
import {MouseEventHandler} from 'react'


export type DialogComponentColor =
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
  color: DialogComponentColor
  /** The button's variant: the MUI's <Button> variant prop */
  variant: 'text' | 'outlined' | 'contained'
  /** The callback for the button click action */
  onClick: MouseEventHandler
}


/**
 * The dialog MobX store exportable type.
 */
export type DialogMobxStoreType = {
  open: boolean
  title?: string
  content?: React.ReactNode
  buttons?: DialogButton[]
  closeCallback?: any
  busy?: boolean
}


/**
 * The dialog project interface type.
 */
export type DialogInterface = {

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
      highlightOK?: boolean, highlightCancel?: boolean, colorOK?: DialogComponentColor,
      colorCancel?: DialogComponentColor
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

