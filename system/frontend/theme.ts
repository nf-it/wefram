import {ThemeOptions} from '@material-ui/core'


interface IWorkspaceTheme extends ThemeOptions {
  notifications: {
    success: string
    error: string
    info: string
    warning: string
  }
}

export const defaultTheme: IWorkspaceTheme = {
  palette: {
    type: 'light',
    primary: {
      main: '#1976d2'
    },
    secondary: {
      main: '#bd3302'
    }
  },

  notifications: {
    success: '#4caf50',
    error: '#d92328',
    info: '#9e9e9e',
    warning: '#ffc107'
  },

  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 800,
      lg: 1440,
      xl: 1920
    }
  },

  overrides: {
    MuiAppBar: {
      root: {
        margin: '.5vmax',
        borderRadius: '.5vmax'
      }
    },

    MuiAccordion: {
      root: {
        '&::before': {
          display: 'none'
        },
        marginBottom: '.2vmax'
      },
      rounded: {
        borderRadius: '.5vmax'
      }
    },

    MuiButton: {
      root: {
        borderRadius: '.5vmax'
      }
    },

    MuiDialogActions: {
      root: {
        padding: '8px 24px'
      }
    },

    MuiFormControl: {
      marginDense: {
        marginTop: 0,
        marginBottom: 0
      }
    },

    MuiOutlinedInput: {
      root: {
        borderRadius: '.5vmax',
        backgroundColor: '#aaa1'
      },
      inputMarginDense: {
        paddingTop: '9px',
        paddingBottom: '9px'
      }
    },

    MuiPaper: {
      rounded: {
        borderRadius: '.5vmax'
      }
    },

    MuiSnackbarContent: {
      root: {
        borderRadius: '.4vmax'
      }
    },

    MuiTypography: {
      h1: {
        fontSize: '2.2rem'
      },
      h2: {
        fontSize: '1.9rem'
      },
      h3: {
        fontSize: '1.8rem'
      },
      h4: {
        fontSize: '1.6rem'
      },
      h5: {
        fontSize: '1.1rem'
      },
      h6: {
        fontSize: '.9rem'
      }
    },

    MuiImageListItem: {
      item: {
        borderRadius: '2px'
      }
    }
  }
}

