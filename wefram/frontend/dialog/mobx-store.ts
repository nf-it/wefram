import React from 'react'
import {makeObservable, observable} from 'mobx'
import {DialogButton} from './types'


/**
 * The MobX store type for the dialog global state.
 */
class Store {

  /** Sets to `true` to open the dialog modal */
  open: boolean = false

  /** The dialog's window's title */
  title?: string = undefined

  /** The dialog's content - the JSX elements */
  content?: React.ReactNode = undefined

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

