const Common = {

  leftTrimSlash: function (s) {
    return s.replace(/^\/+/g, '');
  },

  trimSlashes: function (s) {
    return s.replace(/^\/|\/$/g, '');
  },

  sumArray(arr) {
    return arr.reduce((a, b) => a + b, 0)
  },

  arrayFrom(any) {
    return Array.isArray(any) ? any : [any];
  }

};