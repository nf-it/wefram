Common.UI = {

  nodeAddClasses: (el, classList) => {
    if (!classList)
      return;
    (Array.isArray(classList) ? classList : String(classList).split(' ')).forEach(e => {
      el.classList.add(String(e));
    });
  },

  nodeRemoveClasses: (el, classList) => {
    (Array.isArray(classList) ? classList : [classList]).forEach(e => {
      el.classList.remove(String(e));
    });
  },

  nodeToggleClasses: (el, classList) => {
    (Array.isArray(classList) ? classList : [classList]).forEach(e => {
      el.classList.toggle(String(e));
    });
  },

  nodeApplyProps: (el, props, permitCreateNewProperties = true) => {
    if (!props || !Object.keys(props).length)
      return;
    for (let p in props) {
      if (!props.hasOwnProperty(p))
        continue;
      if (props[p] === undefined || props[p] === null)
        continue;
      if (p === 'visible') {
        if (!props['visible']) {
          el.style.display = 'none';
        }
      } else if (p === 'hidden') {
        if (!!props['hidden']) {
          el.setAttribute('hidden', "");
        }
      } else if ((p === 'disabled') && (props['disabled'])) {
        el.disabled = 'disabled';
      } else if (p === 'attrs') {
        for (let k in props['attrs']) {
          if (!props['attrs'].hasOwnProperty(k))
            continue;
          el.setAttribute(k, props['attrs'][k]);
        }
      } else if (p === 'eventListeners') {
        for (let k in props['eventListeners']) {
          if (!props['eventListeners'].hasOwnProperty(k))
            continue;
          let e = props['eventListeners'][k];
          if (Array.isArray(e)) {
            e.forEach(_e => {
              el.addEventListener(k, _e);
            });
          } else {
            el.addEventListener(k, e);
          }
        }
      } else if (typeof props[p] == 'object') {
        if (permitCreateNewProperties || (p in el)) {
          for (let k in props[p]) {
            if (!props[p].hasOwnProperty(k))
              continue;
            if (permitCreateNewProperties || (k in el[p])) {
              el[p][k] = props[p][k];
            }
          }
        }
      } else if (props[p] !== undefined) {
        if (permitCreateNewProperties || (p in el)) {
          el[p] = props[p];
        }
      }
    }
  },

  nodeIsChildOf: (testingNode, supposedParentNode) => {
    if (supposedParentNode === null || testingNode === null)
      return false;
    if (testingNode.parentElement === supposedParentNode)
      return true;
    let nextParentNode = testingNode.parentElement;
    while (nextParentNode !== null && nextParentNode !== document.documentElement && nextParentNode !== document.body) {
      if (nextParentNode === supposedParentNode)
        return true;
      nextParentNode = nextParentNode.parentElement;
    }
    return false;
  },

  nextSibling: (el, selector) => {
    let sibling = el.nextElementSibling;
    if (!selector)
      return sibling;
    while (sibling) {
      if (sibling.matches(selector))
        return sibling;
      sibling = sibling.nextElementSibling;
    }
    return null;
  },

  previousSibling: (el, selector) => {
    let sibling = el.previousElementSibling;
    if (!selector)
      return sibling;
    while (sibling) {
      if (sibling.matches(selector))
        return sibling;
      sibling = sibling.previousElementSibling;
    }
    return null;
  },

  newNode: (tagName, classList, props = {}, children = [], ns = null) => {
    const node = (ns === null) ? document.createElement(tagName) : document.createElementNS(ns, tagName);
    Common.UI.nodeAddClasses(node, classList);
    Common.UI.nodeApplyProps(node, props);
    if (children && Array.isArray(children) && children.length) {
      children.forEach(child => {
        if (!child)
          return;
        node.append(child);
      });
    }
    node.appendTo = function (parentElement) {
      parentElement.append(node);
      return node;
    };
    return node;
  },

  newNodeNS: (namespace, tagName, classList, props = {}, children = []) => {
    return Common.UI.newNode(tagName, classList, props, children, namespace);
  },

  newDiv: (classList, props, children) => {
    return Common.UI.newNode('div', classList, props, children);
  },

  newSpan: (classList, props, children) => {
    return Common.UI.newNode('span', classList, props, children);
  },

  newSpanText: (innerText, classList, props = {}, children = []) => {
    props = props || {};
    props['innerText'] = innerText;
    return Common.UI.newNode('span', classList, props, children);
  },

  newSpanHTML: (innerHTML, classList, props = {}, children = []) => {
    props = props || {};
    props['innerHTML'] = innerHTML;
    return Common.UI.newNode('span', classList, props, children);
  },

  newStrongText: (innerText, classList, props = {}, children = []) => {
    props = props || {};
    props['innerText'] = innerText;
    return Common.UI.newNode('strong', classList, props, children);
  },

  newParagraph: (innerText, classList, props = {}, children = []) => {
    props = props || {};
    props['innerText'] = innerText;
    return Common.UI.newNode('p', classList, props, children);
  },

  newImg: (src, classList, props = {}) => {
    props = props || {};
    props['src'] = src;
    return Common.UI.newNode('img', classList, props);
  },

  newSVG: (sourceURL, classList, props = {}) => {
    props = props || {};
    const node = Common.UI.newNodeNS("http://www.w3.org/2000/svg", "svg", classList, props);
    node.setAttribute('xmlns', "http://www.w3.org/2000/svg");
    node.setAttribute('preserveAspectRatio', props['preserveAspectRatio'] || "xMidYMid meet");
    node._srcURL = null;
    Object.defineProperty(node, 'src', {
      get: function () {
        return Common.UI._srcURL;
      },
      set: function (value) {
        if (value === Common.UI._srcURL)
          return;
        fetch(value).then(response => {
          response.text().then(content => {
            const temporarySVGouter = document.createElement('div');
            temporarySVGouter.innerHTML = content;
            const svg = temporarySVGouter.children[0];
            // Common.UI.setAttribute('width', svg.getAttribute('width'));
            // Common.UI.setAttribute('height', svg.getAttribute('height'));
            Common.UI.setAttribute('viewBox', svg.getAttribute('viewBox'));
            Common.UI.innerHTML = svg.innerHTML;
          });
        });
      }
    });
    if (sourceURL) {
      node.src = sourceURL;
    }
    return node;
  },

  newButton: (caption, classList, onclick, props = {}, children = []) => {
    props = props || {};
    if (caption) {
      props['innerText'] = caption;
    }
    if (onclick) {
      props['eventListeners'] = props['eventListeners'] || {};
      props['eventListeners']['click'] = onclick;
    }
    return Common.UI.newNode('button', classList, props, children);
  },

  newForm: (classList, onsubmit, props = {}, children = []) => {
    props = props || {};
    if (onsubmit) {
      props['eventListeners'] = props['eventListeners'] || {};
      props['eventListeners']['submit'] = e => {
        e.preventDefault();
        e.stopPropagation();
        onsubmit(e);
      }
    }
    return Common.UI.newNode('form', classList, props, children);
  },

  newInput: (name, value, classList, placeholder, props = {}) => {
    props = props || {};
    if (name) {
      props['name'] = name;
    }
    if (value) {
      props['value'] = String(value);
    }
    if (placeholder) {
      props['placeholder'] = String(placeholder);
    }
    return Common.UI.newNode('input', classList, props);
  },

  newLink: (caption, callback, classList, props = {}) => {
    props = props || {};
    if (typeof (callback) == 'function') {
      props['eventListeners'] = {
        'click': callback
      };
    } else if (typeof (callback) == 'string') {
      props['href'] = callback;
    }
    props['innerText'] = caption;
    return Common.UI.newNode('a', classList, props);
  },

  newSelectOption: (value, caption, selected = false) => {
    return Common.UI.newNode('option', null, {
      innerText: caption,
      value: value === null ? "" : value,
      isnull: value === null,
      selected: !!selected
    });
  }

}