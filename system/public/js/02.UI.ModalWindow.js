UI.ModalWindow = class ModalWindow {

  constructor({
    classList,
    windowMinWidth,
    windowMaxWidth
  }={}) {
    this.windowMaxWidth = windowMaxWidth ?? (System.isSmartphoneScreen() ? '99vw' : '70vw');
    this.windowMinWidth = windowMinWidth ?? (System.isSmartphoneScreen() ? '95vw' : '15vw');
    this.root = UI.newDiv(
      ['SystemModalWindow-root', ...(Common.arrayFrom(classList ?? []) ?? [])],
      {style: {display: 'none'}}
    );
    this.window = UI.newDiv(['SystemModalWindow-window']).appendTo(this.root);
  }

  show() {
    this.window.style.minWidth = this.windowMinWidth;
    this.window.style.maxWidth = this.windowMaxWidth;

    document.body.append(this.root);
    this.root.style.removeProperty('display');
    setTimeout(() => this.window.classList.add('open'), 200);
  }

  close() {
    this.window.classList.remove('open');
    setTimeout(() => this.root.remove(), 250);
  }

};


UI.ModalLayoutWindow = class ModalLayoutWindow extends UI.ModalWindow {
  constructor({
    classList,
    windowMinWidth,
    windowMaxWidth,
    headerText,
    footerControls
  }={}) {
    super({classList, windowMinWidth, windowMaxWidth});

    this.header = ModalLayoutWindow.createHeaderNode().appendTo(this.window);
    this.paper = ModalLayoutWindow.createPaperNode().appendTo(this.window);
    this.footer = ModalLayoutWindow.createFooterNode().appendTo(this.window);

    (headerText) && (this.header.innerText = headerText);
    (footerControls) && (this.footer.append(...Common.arrayFrom(footerControls)));
  }

  get headerText() {
    return this.header.innerText;
  }

  set headerText(value) {
    this.header.innerText = value;
  }

  static createHeaderNode() {
    return UI.newDiv('header');
  }

  static createFooterNode() {
    return UI.newDiv('footer');
  }

  static createPaperNode() {
    return UI.newDiv('paper');
  }

};
