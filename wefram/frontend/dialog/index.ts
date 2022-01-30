/**
 * Provides common dialog facility. Both custom dialogs and most commonly
 * used predefined are provided here.
 *
 * The dialog is a modal interface window, which usually renders the some
 * textual contents and some actions (at least - the "Close" button). The
 * most common cases are some kind of notification or warning, and the
 * confirmation dialog (Yes-No variant).
 *
 * Common case are, for example, displaying dialogs with text messages,
 * or displaying confirmations.
 *
 * For example - the common text dialog:
 *
 * ``
 *    import {dialog} from 'system/dialog'
 *
 *    ...
 *    dialog.showMessage("Hello, I glad to see you", "Hello")
 *    ...
 * ``
 *
 * Or, the second example - show the confirmation:
 *
 * ``
 *    import {dialog} from 'system/dialog'
 *
 *    ...
 *    dialog.showConfirm({
 *      message: "Are you sure to delete those files?",
 *      title: "Deletion",
 *      okCallback: () => {
 *        dialog.hide()
 *        ... // some staff on OK button clicked
 *      }
 *    })
 * ``
 */


export * from './types'
export * from './interface'
export {dialogsStore} from './mobx-store'
