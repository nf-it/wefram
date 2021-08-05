System.requests = {

  requestForURL: function(url, method, params, body) {
    const _url = typeof url == 'string' ? new URL(window.location.origin.concat(url)) : url;

    if (params) {
      for (let paramName in params) {
        if (!params.hasOwnProperty(paramName))
          continue;
        let paramValue = params[paramName];
        if (Array.isArray(paramValue)) {
          const paramNameArr = paramName.concat('[]');
          paramValue.forEach(value => _url.searchParams.append(paramNameArr, String(value)));
        } else {
          _url.searchParams.set(paramName, String(paramValue));
        }
      }
    }

    const authorizationHeader = System.aaa.getCurrentAuthorizationHeader();
    const headers = new Headers();

    authorizationHeader && headers.set('Authorization', authorizationHeader);

    const requestOptions = {
      method,
      body,
      headers
    };

    return new Request(_url, requestOptions);
  },

  axiosOptions: function (params) {
    const authorizationHeader = System.aaa.getCurrentAuthorizationHeader();
    const headers = { };

    authorizationHeader && (headers.Authorization = authorizationHeader);

    return {
      headers,
      params
    }
  },

  get: function (url, params) {
    return axios.get(url, System.requests.axiosOptions(params));
  },

  post: function (url, data, params) {
    return axios.post(url, data, System.requests.axiosOptions(params));
  },

  put: function (url, data, params) {
    return axios.put(url, data, System.requests.axiosOptions(params));
  },

  delete: function (url, params) {
    return axios.delete(url, System.requests.axiosOptions(params));
  },

  options: function (url, params) {
    return axios.options(url, System.requests.axiosOptions(params));
  }

};