System.aaa = {

  localStorageAuthorizationKeyname: 'system.aaa.authorization',

  getCurrentSession: function () {
    const storedSession = localStorage.getItem(System.aaa.localStorageAuthorizationKeyname);
    if (!storedSession)
      return null;
    try {
      return JSON.parse(storedSession);
    } catch {
      localStorage.removeItem(System.aaa.localStorageAuthorizationKeyname);
      console.log("!! invalid AAA session stored to the localStorage, cleaning up !!");
      return null;
    }
  },

  getCurrentAuthorizationToken: function () {
    const currentSession = System.aaa.getCurrentSession();
    if (!currentSession)
      return null;
    return currentSession.token;
  },

  getCurrentAuthorizationHeader: function () {
    const currentToken = System.aaa.getCurrentAuthorizationToken();
    if (!currentToken)
      return null;
    return `Bearer ${currentToken}`;
  }

};