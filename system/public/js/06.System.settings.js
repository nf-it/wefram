System.settings = {

  storage: {},

  set: (app, name, value) => {
    if (System.settings.storage[app] === undefined) {
      System.settings.storage[app] = { };
    }
    System.settings.storage[app][name] = value;
  },

  get: (app, name, defaultValue) => {
    if (!(app in System.settings.storage))
      return defaultValue;
    const appStorage = System.settings.storage[app];
    if (!(name in appStorage))
      return defaultValue;
    return appStorage[name];
  }

};