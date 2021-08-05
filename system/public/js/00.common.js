const Common = {

  leftTrimSlash: function (s) {
    return s.replace(/^\/+/g, '');
  },

  trimSlashes: function (s) {
    return s.replace(/^\/|\/$/g, '');
  }

};