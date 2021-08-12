System.Dialog = class Dialog extends UI.ModalLayoutWindow {

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

    // this.header = UI.newDiv(['SystemDialog-header']);
    // this.footer = UI.newDiv(['SystemDialog-footer']);
    // this.content = UI.newDiv(['SystemDialog-content']);

    // this.window.append(this.header, this.content, this.footer);
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
  }

};