System.api = {

  urlFromPath: function (app, path, version) {
    /*
        The resulting URL will be formatted next way:
        (a) if the version set
        /<app>/v<version>/<path>[?...params]
        for example:
        /myapp/v1/services?search=bubukaka

        (b) if the version omitted
        /<app>/<path>[?...params]
        for example:
        /myapp/services?search=bubuanotherkaka
    */

    const _path = Common.leftTrimSlash(path);
    const urlPath = version
      ? `/api/${app}/v${version}/${_path}`
      : `/api/${app}/${_path}`;
    return new URL(window.location.origin.concat(urlPath));
  },

  get: function ({app, path, version, params}={}) {
    const url = System.api.urlFromPath(app, path, version);
    return System.requests.get(url, params);
  },

  post: function ({app, path, version, data, params}={}) {
    const url = System.api.urlFromPath(app, path, version);
    return System.requests.post(url, data, params);
  },

  put: function ({app, path, version, data, params}={}) {
    const url = System.api.urlFromPath(app, path, version);
    return System.requests.put(url, data, params);
  },

  delete: function({app, path, version, params}) {
    const url = System.api.urlFromPath(app, path, version);
    return System.requests.delete(url, params);
  },

  options: function({app, path, version, params}) {
    const url = System.api.urlFromPath(app, path, version);
    return System.requests.options(url, params);
  }

};