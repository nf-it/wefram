Common.UI.ModalWindow = class ModalWindow {

  constructor({
    classList,
    windowMinWidth,
    windowMaxWidth
  }={}) {
    this.windowMaxWidth = windowMaxWidth ?? (System.isSmartphoneScreen() ? '99vw' : '70vw');
    this.windowMinWidth = windowMinWidth ?? '10vw';
    this.root = Common.UI.newDiv(
      ['SystemModalWindow-root', ...(Common.arrayFrom(classList) ?? [])],
      {style: {display: 'none'}}
    );
    this.window = Common.UI.newDiv(['SystemModalWindow-window']).appendTo(this.root);
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
