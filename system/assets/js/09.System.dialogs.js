System.Dialog = class Dialog extends UI.ModalLayoutWindow {

  constructor({
    title,
    controls,
    contents,
    windowMaxWidth,
    windowMinWidth,
    classList
  }={}) {
    classList = ['SystemDialog', ...(Common.arrayFrom(classList))];
    super({windowMinWidth, windowMaxWidth, classList});

    this.title = title ?? null;
    this.contents = contents ?? null;
    this.controls = controls ?? null;
  }

  show() {
    this.title && (this.headerText = this.title);
    this.controls && (this.footer.append(...Common.arrayFrom(this.controls)));
    this.contents && (this.paper.append(...Common.arrayFrom(this.contents)));
    super.show();
  }

}


System.dialogs = {

  showMessage: (message, {
    title,
    captionOK,
    callbackOK
  }={}) => {
    const dialog = new System.Dialog({title});
    dialog.contents = UI.newParagraph(message);
    dialog.controls = [
      UI.newButton(
        captionOK ?? System.gettext("OK"),
        null,
        callbackOK ?? (() => dialog.close())
      )
    ];
    dialog.show();
    return dialog;
  },

  showConfirm: (message, callbackOK, {
    title,
    captionOK,
    captionCancel,
    callbackCancel
  }={}) => {
    const dialog = new System.Dialog({
      title
    });
    dialog.contents = UI.newParagraph(message);
    dialog.controls = [
      UI.newButton(
        captionOK ?? System.gettext("OK"),
        null,
        callbackOK
      ),
      UI.newButton(
        captionCancel ?? System.gettext("Cancel"),
        null,
        callbackCancel ?? (() => dialog.close())
      )
    ];
    dialog.show();
    return dialog;
  },

  showChoice: (choices, {
    message,
    title,
    cancelButton,
    cancelCaption,
    cancelCallback
  }={}) => {
    const classList = ['SystemDialogChoice']
    const dialog = new System.Dialog({
      classList,
      title
    });
    dialog.contents = [];
    if (message) {
      dialog.contents.push(UI.newParagraph(message));
    }
    choices.forEach(choice => {
      const [caption, callback] = choice;
      dialog.contents.push(UI.newButton(caption, null, () => {
        dialog.close();
        callback();
      }));
    });
    if (cancelButton || cancelCallback) {
      dialog.controls = [
        UI.newButton(
          cancelCaption ?? System.gettext('Cancel'),
          null,
          cancelCallback ?? (() => dialog.close())
        )
      ];
    }
    dialog.show();
  }

};