import React from 'react'
import {
  AppBar,
  ClockTime,
  Menu,
  MenuItem,
  IconButton,
  Toolbar,
  Typography,
  Tooltip,
} from 'system/components'
import {AccountCircle} from '@mui/icons-material'
import {runtime} from 'system/runtime'
import {session} from 'system/aaa'
import {gettext} from 'system/l10n'
import {routingHistory} from 'system/routing'


type LayoutAppbarProps = { }
type LayoutAppbarState = {
  anchorProfileMenu: HTMLElement | null
}


export class LayoutAppbar extends React.Component<LayoutAppbarProps, LayoutAppbarState> {
  state: LayoutAppbarState = {
    anchorProfileMenu: null
  }

  handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>): void => {
    this.setState({anchorProfileMenu: event.currentTarget})
  }

  handleProfileMenuClose = (): void => {
    this.setState({anchorProfileMenu: null})
  }

  handleProfileLogout = (): void => {
    runtime.logoff()
    this.setState({anchorProfileMenu: null})
  }

  handleProfileSignin = () => {
    routingHistory.push(runtime.loginScreenUrl)
  }

  render() {
    return [
      <AppBar position="fixed" key={'__systemAppBar'}>
        <Toolbar>
          <Typography variant="h6" noWrap style={{
            flexGrow: 1,
            textShadow: '0 1px 1px #000D'
          }}>
            {runtime.title}
          </Typography>
          <ClockTime />
          <Tooltip title={session.user?.fullName || gettext('Sign In', 'system.aaa')}>
            <IconButton
              edge="end"
              aria-label={session.user?.fullName || gettext('Sign In', 'system.aaa')}
              aria-controls="profileMenu"
              aria-haspopup="true"
              onClick={this.handleProfileMenuOpen}
              color="inherit"
            >
              <AccountCircle/>
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>,

      <Menu
        key={'__systemAppBarMenu'}
        anchorEl={this.state.anchorProfileMenu}
        anchorOrigin={{vertical: 'top', horizontal: 'right'}}
        id="profileMenu"
        keepMounted
        transformOrigin={{vertical: 'top', horizontal: 'right'}}
        open={this.state.anchorProfileMenu !== null}
        onClose={this.handleProfileMenuClose}
        style={{
          zIndex: 65535
        }}
      >
        {session.authenticated && ([
          <MenuItem key={'__systemAppBarUserDisplayname'}>
            {session.user?.displayName}
          </MenuItem>,
          <MenuItem key={'__systemAppBarUserLogoutButton'} onClick={this.handleProfileLogout}>
            {gettext('Logout', 'system.aaa')}
          </MenuItem>
        ])}
        {!session.authenticated && (
          <MenuItem key={'__systemAppBarUserLoginButton'} onClick={this.handleProfileSignin}>
            {gettext('Sign In', 'system.aaa')}
          </MenuItem>
        )}
      </Menu>
    ]
  }
}