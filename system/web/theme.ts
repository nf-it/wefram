interface ITheme {
  palette: {
    type?: 'light' | 'dark'
    primary: object
    secondary: object
    notifications: {
      success: string
      error: string
      info: string
      warning: string
    }
  }
}

export const defaultTheme: ITheme = {
  palette: {
    type: 'light',
    primary: {
      main: '#1976d2'
    },
    secondary: {
      main: '#bd3302'
    },
    notifications: {
      success: '#4caf50',
      error: '#d92328',
      info: '#9e9e9e',
      warning: '#ffc107'
    }
  }
}

