import {ThemeOptions} from '@mui/material'


const primaryColor = '#0070f0'
const secondaryColor = '#dd2f00'
const disabledColor = '#00000044'
const hintColor = '#4488ff'


export type WeframComponents = {

}

export interface WorkspaceTheme extends ThemeOptions {
  colors: {
    primaryColor: string,
    secondaryColor: string,
    disabledColor: string,
    hintColor: string
  },

  sidebar: {
    background: string,
    itemsColor: string
  },

  notifications: {
    success: string
    error: string
    info: string
    warning: string
  },

  weframComponents: WeframComponents
}


export interface ThemeBreakpoints {
  xs: number
  sm: number
  md: number
  lg: number
  xl: number
}


export const breakpoints: ThemeBreakpoints = {
  xs: 0,
  sm: 600,
  md: 800,
  lg: 1440,
  xl: 1920
}


const workspaceTheme: WorkspaceTheme = {
  colors: {
    primaryColor,
    secondaryColor,
    disabledColor,
    hintColor
  },

  sidebar: {
    background: '#f4f4f4',
    itemsColor: primaryColor
  },

  palette: {
    primary: {
      main: primaryColor
    },
    secondary: {
      main: secondaryColor
    }
  },

  notifications: {
    success: '#4caf50',
    error: '#d92328',
    info: '#9e9e9e',
    warning: '#ffc107'
  },

  breakpoints: {
    keys: ['xs', 'sm', 'md', 'lg', 'xl'],
    values: {
      xs: 575,
      sm: 800,
      md: 960,
      lg: 1440,
      xl: 1920
    }
  },

  weframComponents: {

  },

  components: {
    MuiAlert: {
      styleOverrides: {
        root: {
          padding: '.5vmax 1.5vmax',
          borderRadius: '.4vmax',
          alignItems: 'center'
        }
      }
    },

    MuiAppBar: {
      styleOverrides: {
        root: {
          display: 'flex',
          borderRadius: '6px 6px 0 0',
          zIndex: 1201,
          maxWidth: '19vw',
          right: 'auto',
          justifyContent: 'center',
          background: 'linear-gradient(to left top, #0077FF, #0059B2 120%)',
          color: '#eee',
          boxShadow: '0 0 1vmax #0007',
          // border: '1px solid #0009',
          // top: 'calc(.5vmax + 1px)',
          top: '.5vmax'
        }
      }
    },

    MuiAccordion: {
      styleOverrides: {
        root: {
          '&::before': {
            display: 'none'
          },
          marginBottom: '.2vmax'
        },
        rounded: {
          borderRadius: '.6vmax',
          '&:last-of-type': {
            borderRadius: '.6vmax',
          }
        }
      }
    },

    MuiBackdrop: {
      styleOverrides: {
        root: {
          WebkitBackdropFilter: 'blur(1px)',
          backdropFilter: 'blur(2px)'
        }
      }
    },

    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '.5vmax',
          padding: '7px 15px 6px'
        },
        contained: {
          boxShadow: "0 0 5px #fff9"
        },
        sizeSmall: {
          padding: '3px 9px'
        },
        sizeMedium: {
          padding: '7px 15px 6px'
        },
        sizeLarge: {
          padding: '14px 21px'
        }
      }
    },

    MuiDialog: {
      styleOverrides: {
        container: {
          // WebkitBackdropFilter: 'blur(1px)',
          // backdropFilter: 'blur(2px)'
        }
      }
    },

    MuiDialogActions: {
      styleOverrides: {
        root: {
          padding: '8px 24px'
        }
      }
    },

    MuiImageList: {
      styleOverrides: {
        root: {
          overflowY: 'visible',
          overflowX: 'visible',
          overflow: 'visible'
        }
      }
    },

    MuiImageListItem: {
      styleOverrides: {
        root: {
          border: '2px solid #fff',
          borderRadius: '6px',
          overflow: 'hidden',
          boxShadow: '0 2px 4px #0002'
        }
      }
    },

    MuiFormControl: {
      styleOverrides: {
        marginDense: {
          marginTop: 0,
          marginBottom: 0
        }
      }
    },

    MuiFormControlLabel: {
      styleOverrides: {
        root: {
          marginBottom: 0
        }
      }
    },

    MuiMenu: {
      styleOverrides: {
        paper: {
          borderRadius: '.3vmax !important'
        }
      }
    },

    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: '.5vmax',
          backgroundColor: '#aaa1',
          letterSpacing: 'normal'
        }
      }
    },

    MuiPaper: {
      styleOverrides: {
        rounded: {
          borderRadius: '.6vmax'
        },
        outlined: {
          borderColor: '#00000022'
        }
      }
    },

    MuiSnackbar: {
      styleOverrides: {
        root: {
          borderRadius: '.45vmax',
          zIndex: 65535
        }
      }
    },

    MuiSwitch: {
      styleOverrides: {
        root: {
          padding: '7px'
        },
        track: {
          borderRadius: '14px'
        },
        thumb: {
          backgroundColor: 'white'
        },
        switchBase: {
          '&.Mui-checked': {
            '& + .MuiSwitch-track': {
              backgroundColor: '#27c',
              opacity: 1
            }
          }
        }
      },
    },

    MuiTabs: {
      styleOverrides: {
        indicator: {
          width: '3px',
          borderRadius: '4px'
        }
      }
    },

    MuiTypography: {
      styleOverrides: {
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
          fontSize: '1.15rem'
        },
        h6: {
          fontSize: '1.05rem'
        }
      }
    }
  }
}

export default workspaceTheme
