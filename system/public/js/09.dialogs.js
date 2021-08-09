System.Dialog = class Dialog extends Common.UI.ModalWindow {

  constructor({
    title,
    controls,
    contents,
    windowMaxWidth,
    windowMinWidth
  }={}) {
    super({windowMinWidth, windowMaxWidth});

    this.title = title ?? null;
    this.contents = contents ?? null;
    this.controls = controls ?? null;

    this.header = Common.UI.newDiv(['SystemDialog-header']);
    this.footer = Common.UI.newDiv(['SystemDialog-footer']);
    this.content = Common.UI.newDiv(['SystemDialog-content']);

    this.window.append(this.header, this.content, this.footer);
  }

  show() {
    this.title && (this.header.innerText = this.title);
    this.controls && (this.footer.append(...Common.arrayFrom(this.controls)));
    this.contents && (this.content.append(...Common.arrayFrom(this.contents)));
    super.show();
  }

}


System.dialogs = {

  showMessage: (message, {
    title,
    captionOK,
    callbackOK
  }) => {
    const dialog = new System.Dialog({title});
    dialog.contents = Common.UI.newParagraph(message);
    dialog.controls = [
      Common.UI.newButton(
        captionOK ?? System.gettext("Close"),
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
  }) => {
    const dialog = new System.Dialog({
      title
    });
    dialog.contents = Common.UI.newParagraph(message);
    dialog.controls = [
      Common.UI.newButton(
        captionOK ?? System.gettext("OK"),
        null,
        callbackOK
      ),
      Common.UI.newButton(
        captionCancel ?? System.gettext("Cancel"),
        null,
        callbackCancel ?? (() => dialog.close())
      )
    ];
    dialog.show();
    return dialog;
  }

};